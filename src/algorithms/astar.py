import math
from .min_heap import MinHeap

class AStar:
    """
    A class that implements the A* (A-Star) algorithm to find the shortest path
    using geographical heuristics to optimize the search space.
    """

    def __init__(self, edges, coords):
        """
        Initializes the A* solver with the graph's adjacency list and node coordinates.

        Args:
            edges (list of list): Adjacency list representing the graph. 
                                  Each index corresponds to a vertex, and each 
                                  entry is a list of pairs [destination, weight].
            coords (list of tuple): A list where each index corresponds to a vertex, 
                                    and the value is a tuple of (latitude, longitude).
        """
        self.edges = edges
        self.number_of_vertices = len(edges)
        self.coords = coords

    @staticmethod
    def great_circle(lat1, lon1, lat2, lon2):
        """
        Calculates the great-circle distance between two points on the Earth's surface
        using the Haversine formula.

        Returns:
            float: The distance in meters.
        """
        r_earth = 6371000.0  # Radius of Earth in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0) ** 2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r_earth * c

    @staticmethod
    def euclidean(lat1, lon1, lat2, lon2):
        """
        Calculates a fast Euclidean approximation in meters.
        Valid only for small distances (like urban routing).

        Returns:
            float: The approximate Euclidean distance in meters.
        """
        meters_per_degree_lat = 111320.0
        # Adjust longitude distance scale based on latitude
        lat_rad = math.radians((lat1 + lat2) / 2.0)
        meters_per_degree_lon = math.cos(lat_rad) * meters_per_degree_lat

        dx = (lon2 - lon1) * meters_per_degree_lon
        dy = (lat2 - lat1) * meters_per_degree_lat
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def manhattan(lat1, lon1, lat2, lon2):
        """
        Calculates the Manhattan distance approximation in meters.

        Returns:
            float: The approximate Manhattan distance in meters.
        """
        meters_per_degree_lat = 111320.0
        lat_rad = math.radians((lat1 + lat2) / 2.0)
        meters_per_degree_lon = math.cos(lat_rad) * meters_per_degree_lat

        dx = abs(lon2 - lon1) * meters_per_degree_lon
        dy = abs(lat2 - lat1) * meters_per_degree_lat
        return dx + dy

    def _calculate_heuristic(self, node_idx, target_idx, heuristic_type):
        """
        Helper method to dispatch the chosen heuristic calculation.
        """
        lat1, lon1 = self.coords[node_idx]
        lat2, lon2 = self.coords[target_idx]

        if heuristic_type == "great_circle":
            return self.great_circle(lat1, lon1, lat2, lon2)
        elif heuristic_type == "euclidean":
            return self.euclidean(lat1, lon1, lat2, lon2)
        elif heuristic_type == "manhattan":
            return self.manhattan(lat1, lon1, lat2, lon2)
        else:
            raise ValueError(f"Unknown heuristic: {heuristic_type}")

    def find_shortest_path(self, start, end, heuristic_type="great_circle", on_visit_callback=None):
        """
        Executes the A* algorithm to find the shortest path between a starting 
        node and a destination node.

        Args:
            start (int): The starting node index.
            end (int): The destination node index.
            heuristic_type (str): The heuristic to use ('great_circle', 'euclidean', 'manhattan').
            on_visit_callback (callable, optional): Hook for visualization.

        Returns:
            tuple: (shortest_distance, path_list)
        """
        # g_scores track the actual shortest distance from start to a node
        g_scores = [float("inf")] * self.number_of_vertices
        g_scores[start] = 0

        # f_scores track g(n) + h(n). This dictates the priority in the heap.
        initial_h = self._calculate_heuristic(start, end, heuristic_type)
        
        # MinHeap stores tuples of (f_score, vertex_id)
        min_heap = MinHeap([(initial_h, start)])
        
        visited = set()
        previous_nodes = [None] * self.number_of_vertices

        while len(min_heap.heap) > 0:
            current_f_score, vertex = min_heap.remove()

            # Lazy deletion check
            if vertex in visited:
                continue

            visited.add(vertex)

            if on_visit_callback is not None:
                on_visit_callback(visited, vertex)

            if vertex == end:
                break

            for edge in self.edges[vertex]:
                destination, distance_to_destination = edge

                if destination in visited:
                    continue

                # The cost to reach the neighbor
                tentative_g_score = g_scores[vertex] + distance_to_destination

                # If we found a strictly better path to reach this neighbor
                if tentative_g_score < g_scores[destination]:
                    g_scores[destination] = tentative_g_score
                    previous_nodes[destination] = vertex
                    
                    # Calculate h(n) and f(n)
                    h_score = self._calculate_heuristic(destination, end, heuristic_type)
                    f_score = tentative_g_score + h_score
                    
                    min_heap.insert((f_score, destination))

        path = self.reconstruct_path(previous_nodes, start, end)
        
        return g_scores[end], path

    @staticmethod
    def reconstruct_path(previous_nodes, start, end):
        """
        Reconstructs the path from the starting node to a target node.
        """
        path = []
        current_node = end

        while current_node is not None:
            path.append(current_node)
            current_node = previous_nodes[current_node]

        path.reverse()

        if not path or path[0] != start:
            return []

        return path
