import argparse
import math
import os
import random

import osmnx as ox

from algorithms.dijkstra import Dijkstra
from algorithms.dijkstra_heap import DijkstraHeap
from algorithms.astar import AStar
from visualization import animate_algorithm


def build_adjacency_from_graph(
        graph: ox.graph.Graph, # type: ignore
        weight_attr: str="length"
    ) -> tuple[list[list], dict[int, int], list[int], list[tuple[float, float]]]:
    """
    Converts an OSMnx graph into an adjacency list representation suitable for shortest-path algorithms. It also creates a mapping from graph node IDs to their corresponding indices in the adjacency list, and extracts the coordinates of each node for heuristic calculations in A*.
    Args:
        graph (ox.graph.Graph): The OSMnx graph to convert.
        weight_attr (str): The edge attribute to use as the weight for shortest-path calculations. Defaults to "length".
    Returns:
        A tuple containing the adjacency list, a mapping from graph node IDs to adjacency indices, a list of graph node IDs corresponding to the adjacency indices, and a list of (latitude, longitude) tuples for each node in the graph.
    """
    nodes = list(graph.nodes)
    node_to_idx = {node_id: idx for idx, node_id in enumerate(nodes)}
    coords = []
    for node_id in nodes:
        lat = graph.nodes[node_id]['y']
        lon = graph.nodes[node_id]['x']
        coords.append((lat, lon))

    edge_weights = {}

    for u, v, data in graph.edges(data=True):
        weight = float(data.get(weight_attr, 1.0))
        key = (node_to_idx[u], node_to_idx[v])
        if key not in edge_weights or weight < edge_weights[key]:
            edge_weights[key] = weight

    adjacency = [[] for _ in nodes]
    for (u_idx, v_idx), weight in edge_weights.items():
        adjacency[u_idx].append((v_idx, weight))

    return adjacency, node_to_idx, nodes, coords


def generate_random_points(
        origin_lat: float,
        origin_lon: float,
        radius_m: float,
        count: int,
        seed=None
    ) -> list[tuple[float, float]]:
    """
    Generates random points within a specified radius (in meters) around an origin point defined by latitude and longitude. The points are uniformly distributed within the circular area defined by the radius.
    Args:
        origin_lat (float): The latitude of the origin point.
        origin_lon (float): The longitude of the origin point.
        radius_m (float): The radius in meters within which to generate random points.
        count (int): The number of random points to generate.
        seed (int, optional): A random seed for reproducibility. Defaults to None.
    Returns:
        A list of tuples, where each tuple contains the latitude and longitude of a generated random point.
    """
    rng = random.Random(seed)
    points = []

    meters_per_degree_lat = 111_320.0
    lat_rad = math.radians(origin_lat)
    meters_per_degree_lon = max(1.0, math.cos(lat_rad) * meters_per_degree_lat)

    for _ in range(count):
        angle = rng.random() * 2 * math.pi
        distance = radius_m * math.sqrt(rng.random())
        delta_lat = (distance * math.cos(angle)) / meters_per_degree_lat
        delta_lon = (distance * math.sin(angle)) / meters_per_degree_lon
        points.append((origin_lat + delta_lat, origin_lon + delta_lon))

    return points


def points_to_nodes(
        graph: ox.graph.Graph, # type: ignore
        points: list[tuple[float, float]]
    ) -> list[int]:
    """
    Points the nearest graph nodes for a list of latitude and longitude coordinates.
    Args:
        graph (ox.graph.Graph): The OSMnx graph to query.
        points (list[tuple[float, float]]): A list of (latitude, longitude) tuples representing the points to map to graph nodes.
    Returns:
        A list of graph node IDs corresponding to the nearest nodes for each input point.
    """
    nodes = []
    for lat, lon in points:
        node = ox.distance.nearest_nodes(graph, X=lon, Y=lat)
        nodes.append(node)
    return nodes


def select_best_boarding_node(
        candidate_nodes: list[int],
        node_to_idx: dict[int, int],
        solver: Dijkstra | DijkstraHeap | AStar, dest_idx: int
    ) -> tuple[int | None, float, list[int]]:
    """
    Evaluates each candidate boarding node by computing the shortest path distance to the destination using the provided solver instance.
    Args:
        candidate_nodes (list[int]): A list of candidate boarding node IDs.
        node_to_idx (dict[int, int]): A mapping from graph node IDs to their corresponding indices in the adjacency list.
        solver (Dijkstra | DijkstraHeap | AStar): An instance of the shortest-path algorithm to use for distance calculations.
        dest_idx (int): The index of the destination node in the adjacency list.
    Returns:
        A tuple containing the best boarding node ID (or None if no valid candidates), the shortest distance to the destination, and the path from the boarding node to the destination as a list of node indices.
    """
    best_node = None
    best_distance = float("inf")
    best_path = []

    for node in candidate_nodes:
        start_idx = node_to_idx[node]
        distance, path = solver.find_shortest_path(start_idx, dest_idx)

        if math.isinf(distance):
            continue

        if distance < best_distance:
            best_distance = distance
            best_node = node
            best_path = path

    return best_node, best_distance, best_path


def create_solver(
        algorithm_name: str,
        adjacency: list[list],
        coordinates: list(tuple[float, float]) | None=None
    ) -> Dijkstra | DijkstraHeap | AStar:
    """
    Factory function to create a solver instance based on the specified algorithm name.
    Args:
        algorithm_name (str): The name of the algorithm to use.
        adjacency (list[list]): The adjacency list representing the graph.
        coordinates (tuple[int], optional): The coordinates of the nodes, required for A*.
    Returns:
        An instance of the specified algorithm class.
    Raises:
        ValueError: If an unsupported algorithm name is provided.
    """
    if algorithm_name == "dijkstra":
        return Dijkstra(adjacency)
    if algorithm_name == "dijkstra_heap":
        return DijkstraHeap(adjacency)
    if algorithm_name == "astar":
        return AStar(adjacency, coordinates)
    raise ValueError(f"Unsupported algorithm: {algorithm_name}")


def load_graph(args: argparse.Namespace) -> ox.graph.Graph: # type: ignore
    """
    Loads a graph based on the provided command-line arguments. The graph can be loaded from a local .graphml file, downloaded using a place name, or dynamically generated around the midpoint between the origin and destination coordinates.
    Args:
        args (argparse.Namespace): The command-line arguments containing the graph loading parameters.
    Returns:
        An OSMnx graph object representing the loaded graph.
    """
    if args.graphml:
        return ox.load_graphml(args.graphml)

    if args.place:
        return ox.graph_from_place(args.place, network_type="drive")

    mid_lat = (args.origin_lat + args.dest_lat) / 2
    mid_lon = (args.origin_lon + args.dest_lon) / 2

    dist_degrees = math.sqrt((args.origin_lat - args.dest_lat)**2 \
        + (args.origin_lon - args.dest_lon)**2)
    dist_meters = dist_degrees * 111320.0
    
    dynamic_radius = (dist_meters / 2) + args.walk_radius

    print(f"Loading dynamic map at midpoint with {dynamic_radius:.0f}m radius...")
    
    return ox.graph_from_point(
        (mid_lat, mid_lon),
        dist=dynamic_radius,
        network_type="drive",
    )


def save_animation(html, output_path: str) -> None:
    """
    Saves the generated HTML animation to the specified output path, creating any necessary directories along the way.
    Args:
        html (IPython.display.HTML): The HTML content to save.
        output_path (str): The file path where the HTML content should be saved.
    """
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    html_content = html.data if hasattr(html, "data") else str(html)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(html_content)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate random boarding points and visualize Dijkstra search."
    )
    parser.add_argument(
        "--place",
        "-p",
        default=None,
        help="Place name for downloading a graph with OSMnx.",
    )
    parser.add_argument(
        "--graphml",
        "-g",
        default=None,
        help="Path to a local .graphml file to load a graph from.",
    )
    parser.add_argument(
        "--origin-lat",
        "-olt",
        type=float,
        default=-23.5505,
        help="Origin latitude.",
    )
    parser.add_argument(
        "--origin-lon",
        "-oln",
        type=float,
        default=-46.6333,
        help="Origin longitude.",
    )
    parser.add_argument(
        "--dest-lat",
        "-dlt",
        type=float,
        default=-23.5631,
        help="Destination latitude.",
    )
    parser.add_argument(
        "--dest-lon",
        "-dln",
        type=float,
        default=-46.6556,
        help="Destination longitude.",
    )
    parser.add_argument(
        "--walk-radius",
        "-r",
        type=float,
        default=500.0,
        help="Walking radius in meters for candidate boarding points.",
    )
    parser.add_argument(
        "--candidates",
        "-c",
        type=int,
        default=30,
        help="Number of random boarding candidates to generate.",
    )
    parser.add_argument(
        "--algorithm",
        "-a",
        choices=["dijkstra", "dijkstra_heap"],
        default="dijkstra_heap",
        help="Shortest-path algorithm to visualize.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/processed/dijkstra_animation.html",
        help="Path to write the HTML animation.",
    )
    parser.add_argument(
        "--seed",
        "-s",
        type=int,
        default=42,
        help="Random seed for candidate generation.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    graph = load_graph(args)
    graph = ox.distance.add_edge_lengths(graph)

    adjacency, node_to_idx, idx_to_node, coords = build_adjacency_from_graph(graph)

    origin_node = ox.distance.nearest_nodes(graph, X=args.origin_lon, Y=args.origin_lat)
    dest_node = ox.distance.nearest_nodes(graph, X=args.dest_lon, Y=args.dest_lat)

    random_points = generate_random_points(
        args.origin_lat,
        args.origin_lon,
        args.walk_radius,
        args.candidates,
        seed=args.seed,
    )
    candidate_nodes = points_to_nodes(graph, random_points)
    candidate_nodes = list(dict.fromkeys(candidate_nodes))

    if not candidate_nodes:
        raise RuntimeError("No boarding candidates were generated.")

    solver = create_solver(args.algorithm, adjacency, coords)
    dest_idx = node_to_idx[dest_node]

    candidate_indices = [node_to_idx[node] for node in candidate_nodes]

    html = animate_algorithm(
        G=graph,
        solver_instance=solver,
        origin_graph_node=origin_node,
        dest_graph_node=dest_node,
        dest_idx=dest_idx,
        candidate_indices=candidate_indices,
        index_to_node=idx_to_node,
        walk_radius=args.walk_radius
    )
    
    save_animation(html, args.output)

    print(f"Origin node: {origin_node}")
    print(f"Destination node: {dest_node}")
    print(f"Valid Candidates found: {len(candidate_nodes)}")
    print(f"Animation saved to: {args.output}")

if __name__ == "__main__":
    main()
