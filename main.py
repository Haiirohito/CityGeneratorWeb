from Algorithms import road_generation

road = road_generation.AddRoad()

road.add_node(0, 0)
road.add_node(5, 20)
road.add_node(30, 25)
road.add_node(40, 18)
road.add_node(25, 0)

road.add_edge("n0", "n1", "bi")
road.add_edge("n1", "n2", "bi")
road.add_edge("n2", "n3", "bi")
road.add_edge("n3", "n4", "bi")
road.add_edge("n4", "n0", "bi")

# road.export()


path = "Algorithms/road_networks/road_network_20250602_002559.json"

nodes, graph = road_generation.graph_from_json(path)


for i, v in nodes.items():
    print(f"{i}: {v}")


for i, v in graph.items():
    print(f"{i}: {v}")

road_generation.display_road_network(nodes, graph)
