import math
import random
import heapq
import matplotlib.pyplot as plt
from noise import pnoise2, pnoise1


### ========== 1. BLOCK/GRID TYPE ========== ###
class Block:
    def __init__(self, x, y, width, height, depth=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth

    def get_edges(self):
        return [
            ((self.x, self.y), (self.x + self.width, self.y)),
            (
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.height),
            ),
            (
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height),
            ),
            ((self.x, self.y + self.height), (self.x, self.y)),
        ]


def subdivide(block, min_size=30, max_depth=4):
    blocks = []
    if block.depth >= max_depth or (
        block.width < 2 * min_size and block.height < 2 * min_size
    ):
        return [block]

    split_vertically = block.width > block.height
    if split_vertically and block.width > 2 * min_size:
        split = random.randint(min_size, int(block.width - min_size))
        b1 = Block(block.x, block.y, split, block.height, block.depth + 1)
        b2 = Block(
            block.x + split, block.y, block.width - split, block.height, block.depth + 1
        )
        blocks += subdivide(b1, min_size, max_depth)
        blocks += subdivide(b2, min_size, max_depth)
    elif not split_vertically and block.height > 2 * min_size:
        split = random.randint(min_size, int(block.height - min_size))
        b1 = Block(block.x, block.y, block.width, split, block.depth + 1)
        b2 = Block(
            block.x, block.y + split, block.width, block.height - split, block.depth + 1
        )
        blocks += subdivide(b1, min_size, max_depth)
        blocks += subdivide(b2, min_size, max_depth)
    else:
        blocks.append(block)

    return blocks


def generate_block_roads(area=(0, 0, 400, 400)):
    root_block = Block(*area)
    blocks = subdivide(root_block, min_size=40, max_depth=5)
    edges = set()
    for block in blocks:
        for e in block.get_edges():
            edges.add(e)
    return list(edges)


### ========== 2. ORGANIC GROWTH TYPE ========== ###
class RoadSegment:
    def __init__(self, start, direction, length=10, priority=0, parent=None):
        self.start = start
        self.direction = direction
        self.length = length
        self.priority = priority
        self.parent = parent  # To help smooth the path

    def end_point(self):
        dx = self.length * math.cos(self.direction)
        dy = self.length * math.sin(self.direction)
        return (self.start[0] + dx, self.start[1] + dy)

    def __lt__(self, other):
        return self.priority < other.priority


def generate_organic_roads(start_pos=(0, 0), max_segments=400, merge_distance=12):
    road_queue = []
    final_segments = []
    endpoints = []

    # Radial growth: 360° spread
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        heapq.heappush(road_queue, RoadSegment(start_pos, rad, length=25, priority=0))

    while road_queue and len(final_segments) < max_segments:
        current = heapq.heappop(road_queue)
        current_end = current.end_point()

        # Avoid clustering: reduce merging near dense clusters
        if any(math.dist(current_end, pt) < merge_distance for pt in endpoints):
            continue

        final_segments.append(current)
        endpoints.append(current_end)

        # Terminate some paths probabilistically
        if random.random() < 0.03 + current.priority / (max_segments * 1.5):
            continue

        # Organic direction smoothing with memory of parent
        parent_dir = current.direction
        if current.parent:
            parent_dir = current.direction * 0.6 + current.parent.direction * 0.4

        for angle_offset in [0, math.radians(18), math.radians(-18)]:
            if random.random() > max(0.3, 1 - current.priority / 100):
                continue

            curve_bias = random.uniform(-0.15, 0.15)
            smooth_dir = parent_dir + angle_offset + curve_bias

            length = random.uniform(14, 22 if current.priority < 10 else 14)
            child = RoadSegment(
                current_end, smooth_dir, length, current.priority + 1, parent=current
            )
            heapq.heappush(road_queue, child)

    return [(seg.start, seg.end_point()) for seg in final_segments]


### ========== 3. RADIAL TYPE ========== ###
def generate_radial_roads(
    center=(200, 200),
    base_radius=180,
    ring_count=6,
    max_spoke_count=18,
    jitter=6,
    shortcut_prob=0.08,
):
    edges = []
    seed = random.randint(0, 1000)

    def radial_noise(val, scale=0.2):
        return pnoise1(val * scale + seed)

    ring_radii = []
    for i in range(1, ring_count + 1):
        scale = base_radius * (i / ring_count)
        noise = radial_noise(i) * 20
        ring_radii.append(scale + noise)

    # Generate varying spokes per ring (less uniform)
    for i in range(ring_count):
        radius = ring_radii[i]
        next_radius = ring_radii[i + 1] if i + 1 < ring_count else radius + 25

        # Fewer spokes in outer rings
        spoke_count = max_spoke_count - i
        angle_step = 2 * math.pi / spoke_count
        for j in range(spoke_count):
            angle = j * angle_step + random.uniform(-0.05, 0.05)
            angle_next = (j + 1) * angle_step + random.uniform(-0.05, 0.05)

            r1 = radius + random.uniform(-jitter, jitter)
            r2 = radius + random.uniform(-jitter, jitter)
            r3 = next_radius + random.uniform(-jitter, jitter)

            # Current and next point on same ring
            x1 = center[0] + r1 * math.cos(angle)
            y1 = center[1] + r1 * math.sin(angle)
            x2 = center[0] + r2 * math.cos(angle_next)
            y2 = center[1] + r2 * math.sin(angle_next)

            # Radial connection to next ring
            x3 = center[0] + r3 * math.cos(angle)
            y3 = center[1] + r3 * math.sin(angle)

            edges.append(((x1, y1), (x2, y2)))
            edges.append(((x1, y1), (x3, y3)))

            # Occasional diagonal shortcut
            if random.random() < shortcut_prob:
                x_diag = center[0] + r3 * math.cos(angle_next)
                y_diag = center[1] + r3 * math.sin(angle_next)
                edges.append(((x3, y3), (x_diag, y_diag)))

    return edges


### ========== VISUALIZER ========== ###
def draw_roads(edges, title="Road Network"):
    plt.figure(figsize=(10, 10))
    for start, end in edges:
        x_vals = [start[0], end[0]]
        y_vals = [start[1], end[1]]
        plt.plot(x_vals, y_vals, "k-", linewidth=1.2)
    plt.axis("equal")
    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(False)
    plt.show()


### ========== MAIN SELECTOR ========== ###
if __name__ == "__main__":
    mode = (
        input("Choose road generation type (block / organic / radial): ")
        .strip()
        .lower()
    )

    if mode == "block":
        roads = generate_block_roads()
        draw_roads(roads, title="Block/Grid Road Network")

    elif mode == "organic":
        roads = generate_organic_roads()
        draw_roads(roads, title="Organic Road Network")

    elif mode == "radial":
        roads = generate_radial_roads()
        draw_roads(roads, title="Radial Road Network")

    else:
        print("Invalid mode selected. Choose 'block', 'organic', or 'radial'.")
