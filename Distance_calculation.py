from dijkstar import Graph, find_path
from math import sqrt
import numpy as np


def Dijkstra_algorithm(roads, construction_sites_coords, storage_sites_coords, scale):
    # Create a graph
    graph = Graph()

    # Add edges to the graph
    for road in roads:
        node_one = (road["x1"], road["y1"])
        node_two = (road["x2"], road["y2"])
        node_distance = sqrt((node_two[0] - node_one[0])**2 + (node_two[1] - node_one[1])**2)
        graph.add_edge(node_one, node_two, node_distance)
        graph.add_edge(node_two, node_one, node_distance)

    # Create a distance matrix
    distance_matrix_list = []
    for storage_site in storage_sites_coords:
        storage_site_distances = []

        for construction_site in construction_sites_coords:
            construction_site_distance = find_path(graph, storage_site, construction_site).total_cost
            storage_site_distances.append(construction_site_distance)

        distance_matrix_list.append(storage_site_distances)

    distance_matrix_no_scale = np.array(distance_matrix_list)

    distance_matrix = distance_matrix_no_scale * scale


    return distance_matrix
