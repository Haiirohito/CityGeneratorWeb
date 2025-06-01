import os
import json
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt


class AddRoad:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.deleted_nodes = []
        self.graph = defaultdict(
            list
        )  # adjacency list: node_id -> list of (neighbor_id, edge_info)

        self.node_count = 0
        self.network_count = 0

    def add_node(self, x, y):
        if self.deleted_nodes:
            reused_id = self.deleted_nodes.pop(0)
            node_id = f"n{reused_id}"
        else:
            node_id = f"n{self.node_count}"
            self.node_count += 1
        self.nodes[node_id] = (x, y)
        return node_id

    def delete_node(self, node_id):
        if node_id in self.nodes:
            del self.nodes[node_id]

            # Remove edges involving this node from edges list
            self.edges = [
                edge
                for edge in self.edges
                if edge["from"] != node_id and edge["to"] != node_id
            ]

            # Remove from graph adjacency
            if node_id in self.graph:
                del self.graph[node_id]
            for neighbors in self.graph.values():
                neighbors[:] = [n for n in neighbors if n[0] != node_id]

            # Add node id back for reuse
            self.deleted_nodes.append(int(node_id[1:]))

            return node_id
        else:
            print(f"Node {node_id} does not exist.")
            return None

    def add_edge(self, begin, end, direction="uni"):
        road_directions = {"uni", "bi"}

        if direction not in road_directions:
            raise ValueError(
                f"Invalid road direction type: {direction} allowed values: {road_directions}"
            )

        if begin not in self.nodes:
            print(f"Begin Node: {begin} not in available nodes")
            return
        if end not in self.nodes:
            print(f"End Node: {end} not in available nodes")
            return

        x = self.nodes[begin]
        y = self.nodes[end]

        length = abs(x[0] - y[0]) + abs(x[1] - y[1])

        edge_info = {"length": length, "direction": direction}

        # Add to edges list for export
        self.edges.append(
            {"from": begin, "to": end, "length": length, "direction": direction}
        )

        # Add to adjacency graph for algorithms
        self.graph[begin].append((end, edge_info))
        if direction == "bi":
            self.graph[end].append((begin, edge_info))

    def export(self, path="road_networks", name=None):
        base_dir = os.path.dirname(__file__)
        full_path = os.path.join(base_dir, path)

        os.makedirs(full_path, exist_ok=True)

        if name is None:
            name = datetime.now().strftime("road_network_%Y%m%d_%H%M%S")

        with open(os.path.join(full_path, name + ".json"), "w") as f:
            json.dump(
                {"nodes": self.nodes, "edges": self.edges},
                f,
                indent=2,
                separators=(",", ": "),
            )


def graph_from_json(path):
    with open(path) as f:
        data = json.load(f)

    nodes = data["nodes"]
    edges = data["edges"]
    graph = defaultdict(list)

    for edge in edges:
        frm, to, length, direction = (
            edge["from"],
            edge["to"],
            edge["length"],
            edge["direction"],
        )
        graph[frm].append((to, {"length": length, "direction": direction}))
        if direction == "bi":
            graph[to].append((frm, {"length": length, "direction": direction}))

    return nodes, graph


def display_road_network(nodes, graph):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_facecolor("#f9f9f9")  # light background for modern minimal look

    # Plot nodes
    for node_id, (x, y) in nodes.items():
        ax.scatter(
            x, y, color="#1f77b4", s=80, edgecolors="white", linewidth=1.5, zorder=3
        )
        ax.text(
            x + 0.3,
            y + 0.3,
            node_id,
            fontsize=10,
            fontweight="medium",
            color="#333333",
            zorder=4,
        )

    # Plot edges
    for from_node, neighbors in graph.items():
        x_start, y_start = nodes[from_node]
        for to_node, edge_info in neighbors:
            x_end, y_end = nodes[to_node]

            # Soft gray line for edges
            ax.plot(
                [x_start, x_end],
                [y_start, y_end],
                color="#bbbbbb",
                linewidth=1,
                zorder=1,
            )

            # Subtle arrow for uni-directional edges
            if edge_info.get("direction") == "uni":
                ax.annotate(
                    "",
                    xy=(x_end, y_end),
                    xytext=(x_start, y_start),
                    arrowprops=dict(
                        arrowstyle="->",
                        color="#ff6f61",
                        lw=1.5,
                        shrinkA=5,
                        shrinkB=5,
                    ),
                    zorder=5,
                )

    # Clean axis
    ax.set_aspect("equal")
    ax.grid(False)
    ax.axis("off")  # Hide axes for minimalism

    # Add a subtle border around the plot
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    plt.show()


# For testing
if __name__ == "__main__":
    road = AddRoad()

    road.add_node(50, 50)
    road.add_node(40, 50)
    road.add_node(0, 0)
    road.add_node(10, 500)
    road.add_node(20, 53)
    road.add_node(56, 123)

    road.add_edge("n1", "n3", "uni")
    road.add_edge("n1", "n2", "bi")
    road.add_edge("n0", "n2", "bi")

    print("Nodes:", road.nodes)
    print("Edges:", road.edges)
    print("Graph adjacency:")
    for node, neighbors in road.graph.items():
        print(f"  {node}: {neighbors}")

    road.export()
