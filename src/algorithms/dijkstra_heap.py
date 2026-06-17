from .min_heap import MinHeap
from .dijkstra import Dijkstra

class DijkstraHeap(Dijkstra):
    """
    A class that implements Dijkstra's algorithm optimized with a Min-Heap.
    Inherits initialization and path reconstruction from the standard Dijkstra class.
    """

    def __init__(self, edges):
        super().__init__(edges)

    def find_shortest_path(self, start, end, on_visit_callback=None):
        """
        Executes Dijkstra's algorithm using a Min-Heap to find the shortest path.
        """
        min_distances = [float("inf") for _ in range(self.number_of_vertices)]
        min_distances[start] = 0
        
        previous_nodes = [None] * self.number_of_vertices
        visited = set()

        min_heap = MinHeap([(0, start)]) # Tupla (distância_atual, vértice)

        while len(min_heap.heap) > 0:
            current_min_distance, vertex = min_heap.remove()

            if vertex in visited:
                continue

            visited.add(vertex)

            if on_visit_callback is not None:
                on_visit_callback(visited, vertex)

            # Early exit
            if vertex == end:
                break

            for edge in self.edges[vertex]:
                destination, distance_to_destination = edge

                if destination in visited:
                    continue

                new_path_distance = current_min_distance + distance_to_destination

                if new_path_distance < min_distances[destination]:
                    min_distances[destination] = new_path_distance
                    previous_nodes[destination] = vertex
                    min_heap.insert((new_path_distance, destination)) # lazy deletion

        path = self.reconstruct_path(previous_nodes, start, end)

        return min_distances[end], path
