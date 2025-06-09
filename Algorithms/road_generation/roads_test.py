import math
import heapq
import matplotlib.pyplot as plt


# road segment class
class RoadSegment:
    def __init__(self, start, direction, length=10, priority=0):
        self.start = start
        self.direction = direction
        self.length = length
        self.priority = priority

    def end_point(self):
        dx = self.length * math.cos(self.direction)
        dy = self.length * math.sin(self.direction)
        return (self.start[0] + dx, self.start[1] + dy)

    def __lt__(self, other):
        return self.priority < other.priority


# constraint checker
def is_valid_segment(new_seg, existing_segments, min_distance=5):
    new_end = new_seg.end_point()
    for seg in existing_segments:
        end = seg.end_point()
        dist = math.hypot(new_end[0] - end[0], new_end[1] - end[1])
        if dist < min_distance:
            return False
    return True


# global growth rules
def generate_new_segments(segment):
    new_segment = []
    base_priority = segment.priority + 1

    # try going stright, left and right
    branch_angles = [0, math.radians(30), math.radians(-30), math.radians(180)]

    for angle in branch_angles:
        new_direction = segment.direction + angle
        new_seg = RoadSegment(
            segment.end_point(), new_direction, priority=base_priority
        )
        new_segment.append(new_seg)

    return new_segment


# main generator
# def generate_road_network(start_pos=(0, 0), start_dir=0, max_segments=100):
#     road_queue = []
#     final_segments = []

#     start_segment = RoadSegment(start_pos, start_dir, priority=0)
#     heapq.heappush(road_queue, start_segment)

#     while road_queue and len(final_segments) < max_segments:
#         current = heapq.heappop(road_queue)

#         if is_valid_segment(current, final_segments):
#             final_segments.append(current)
#             new_segments = generate_new_segments(current)

#             for seg in new_segments:
#                 heapq.heappush(road_queue, seg)

#     return final_segments

# merge nearby end points


def generate_road_network(
    start_pos=(0, 0), start_dir=0, max_segments=100, merge_distance=5
):
    road_queue = []
    final_segments = []

    start_segment = RoadSegment(start_pos, start_dir, priority=0)
    heapq.heappush(road_queue, start_segment)

    while road_queue and len(final_segments) < max_segments:
        current = heapq.heappop(road_queue)
        current_end = current.end_point()

        # Snap to existing endpoint if nearby
        for seg in final_segments:
            end = seg.end_point()
            dist = math.hypot(current_end[0] - end[0], current_end[1] - end[1])
            if dist < merge_distance:
                # Replace endpoint with average (merge)
                snapped_point = (
                    (current_end[0] + end[0]) / 2,
                    (current_end[1] + end[1]) / 2,
                )

                # Recalculate current to end at the snapped_point
                new_dir = math.atan2(
                    snapped_point[1] - current.start[1],
                    snapped_point[0] - current.start[0],
                )
                current = RoadSegment(
                    current.start,
                    new_dir,
                    length=math.hypot(
                        snapped_point[0] - current.start[0],
                        snapped_point[1] - current.start[1],
                    ),
                    priority=current.priority,
                )
                break

        if is_valid_segment(current, final_segments):
            final_segments.append(current)
            new_segments = generate_new_segments(current)
            for seg in new_segments:
                heapq.heappush(road_queue, seg)

    return final_segments


# visualization
def visualize_road_network(segments):
    plt.figure(figsize=(8, 8))
    endpoints = set()

    for seg in segments:
        x1, y1 = seg.start
        x2, y2 = seg.end_point()
        plt.plot([x1, x2], [y1, y2], "k-")
        endpoints.add((round(x2, 1), round(y2, 1)))  # Collect rounded endpoints

    for x, y in endpoints:
        plt.plot(x, y, "ro", markersize=4)  # draw endpoints

    plt.axis("equal")
    plt.title("Procedurally Generated Road Network with Intersections")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    road_segments = generate_road_network(merge_distance=10, max_segments=1000)
    visualize_road_network(road_segments)
