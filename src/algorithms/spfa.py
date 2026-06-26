from collections import deque

class SPFA:
    """
    A class that implements the Shortest Path Faster Algorithm (SPFA).
    An optimized version of Bellman-Ford using a queue to avoid redundant relaxations.
    """

    def __init__(self, edges):
        """
        Initializes the SPFA solver with the graph's adjacency list.

        Args:
            edges (list of list): Adjacency list representing the graph.
        """
        self.edges = edges
        self.number_of_vertices = len(edges)

    def find_shortest_path(self, start, end, on_visit_callback=None):
        """
        Executes the SPFA algorithm to find the shortest path.
        Also capable of handling negative edge weights (unlike Dijkstra).

        Returns:
            tuple: (shortest_distance, path_list)
        """
        min_distances = [float("inf") for _ in range(self.number_of_vertices)]
        min_distances[start] = 0

        previous_nodes = [None] * self.number_of_vertices
        
        in_queue = [False] * self.number_of_vertices
        
        relaxation_count = [0] * self.number_of_vertices

        queue = deque([start])
        in_queue[start] = True
        
        visited = set()

        while queue:
            vertex = queue.popleft()
            in_queue[vertex] = False
            
            visited.add(vertex)
            if on_visit_callback is not None:
                on_visit_callback(visited, vertex)

            for edge in self.edges[vertex]:
                destination, distance_to_destination = edge

                new_path_distance = min_distances[vertex] + distance_to_destination

                if new_path_distance < min_distances[destination]:
                    min_distances[destination] = new_path_distance
                    previous_nodes[destination] = vertex

                    if not in_queue[destination]:
                        queue.append(destination)
                        in_queue[destination] = True
                        relaxation_count[destination] += 1
                        
                        if relaxation_count[destination] >= self.number_of_vertices:
                            raise ValueError("Graph contains a negative-weight cycle")

        path = self._reconstruct_path(previous_nodes, start, end)

        return min_distances[end], path

    @staticmethod
    def _reconstruct_path(previous_nodes, start, end):
        path = []
        current_node = end
        while current_node is not None:
            path.append(current_node)
            current_node = previous_nodes[current_node]
        path.reverse()
        return path if path and path[0] == start else []