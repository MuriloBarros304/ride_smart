def getVertexWithMinDistance(distances, visited):
    """
    Helper function to find the vertex with the smallest known distance that has not been visited.

    Args:
        distances (list): A list of the shortest known distances to each vertex.
        visited (set): A set of vertices that have already been visited.

    Returns:
        tuple: The index of the vertex with the smallest distance and its distance value.
    """
    currentMinDistance = float("inf")
    vertex = -1

    # Iterate over all vertices to find the one with the smallest distance.
    for vertexIdx, distance in enumerate(distances):
        # Skip the vertex if it has already been visited.
        if vertexIdx in visited:
            continue

        # Update the current minimum distance and vertex if a smaller distance is found.
        if distance <= currentMinDistance:
            vertex = vertexIdx
            currentMinDistance = distance

    return vertex, currentMinDistance


def dijkstrasAlgorithmWithPaths(start, edges):
    """
    Implements Dijkstra's algorithm to find the shortest paths from a starting node to all other nodes in a graph.
    Additionally, it tracks the path to each node using a predecessor list.

    Args:
        start (int): The starting node index.
        edges (list of list): Adjacency list representing the graph. Each index corresponds to a vertex,
                              and each entry is a list of pairs [destination, weight].

    Returns:
        tuple: A tuple containing:
            - minDistances (list): A list of the shortest distances from the starting node to each node.
                                   If a node is unreachable, its distance is `inf`.
            - previousNodes (list): A list where each index points to the predecessor of the node
                                    in the shortest path. `None` if no path exists.
    """
    numberOfVertices = len(edges)

    # Initialize the minimum distances with infinity, except for the starting node (distance 0).
    minDistances = [float("inf") for _ in range(numberOfVertices)]
    minDistances[start] = 0

    # Set of visited nodes to avoid re-processing.
    visited = set()

    # Predecessor list to track the path to each node.
    previousNodes = [None] * numberOfVertices

    # Iterate until all nodes are processed or no more reachable nodes exist.
    while len(visited) != numberOfVertices:
        # Find the unvisited node with the smallest known distance.
        vertex, currentMinDistance = getVertexWithMinDistance(minDistances, visited)

        # If the smallest distance is infinity, remaining nodes are unreachable.
        if currentMinDistance == float("inf"):
            break

        # Mark the current node as visited.
        visited.add(vertex)

        # Update distances for all neighbors of the current node.
        for edge in edges[vertex]:
            destination, distanceToDestination = edge

            # Skip if the neighbor is already visited.
            if destination in visited:
                continue

            # Calculate the new potential path distance.
            newPathDistance = currentMinDistance + distanceToDestination
            currentDestinationDistance = minDistances[destination]

            # Update the shortest distance and the predecessor if the new path is shorter.
            if newPathDistance <= currentDestinationDistance:
                minDistances[destination] = newPathDistance
                previousNodes[destination] = vertex  # Update predecessor

    return minDistances, previousNodes

def reconstructPath(previousNodes, start, end):
    path = []
    currentNode = end

    while currentNode is not None:  # Trace back to the start node
        path.append(currentNode)
        currentNode = previousNodes[currentNode]

    path.reverse()  # Reverse the path to get it in the correct order

    # If the start node is not in the path, the destination is unreachable
    if path[0] != start:
        return []

    return path
