import math
from .min_heap import MinHeap


class BlockAStar:
    """
    A class that implements the Block A* algorithm, a hierarchical variant of A*
    that partitions the graph into geographic blocks (cells of a uniform lat/lon grid).

    """

    def __init__(self, edges, coords, block_size_deg: float = 0.01):
        self.edges = edges
        self.coords = coords
        self.number_of_vertices = len(edges)
        self.block_size = block_size_deg

        # Build the block partitioning
        self._node_to_block: list[tuple[int, int]] = []   # node → (row, col)
        self._block_to_nodes: dict[tuple[int, int], list[int]] = {}
        self._build_blocks()

        # Build a lightweight block-level graph
        self._block_graph: dict[tuple[int, int], dict[tuple[int, int], float]] = {}
        self._block_centres: dict[tuple[int, int], tuple[float, float]] = {}
        self._build_block_graph()

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def _coord_to_block(self, lat: float, lon: float) -> tuple[int, int]:
        """Map a (lat, lon) coordinate to a (row, col) block index."""
        row = int(math.floor(lat / self.block_size))
        col = int(math.floor(lon / self.block_size))
        return row, col

    def _build_blocks(self):
        """Assign every node to its geographic block."""
        for idx, (lat, lon) in enumerate(self.coords):
            block = self._coord_to_block(lat, lon)
            self._node_to_block.append(block)
            self._block_to_nodes.setdefault(block, []).append(idx)

    def _build_block_graph(self):
        """
        Construct the coarse block-level graph.

        For each directed road edge (u → v) that crosses a block boundary,
        record an edge between the two blocks with the road weight as cost,
        keeping only the minimum weight seen so far.
        """
        for u, neighbours in enumerate(self.edges):
            block_u = self._node_to_block[u]
            for edge in neighbours:
                v, weight = edge[0], edge[1]
                block_v = self._node_to_block[v]
                if block_u == block_v:
                    continue  # intra-block edge; not needed at block level
                # Update minimum inter-block weight (undirected for the coarse graph)
                for src, dst in ((block_u, block_v), (block_v, block_u)):
                    if src not in self._block_graph:
                        self._block_graph[src] = {}
                    if dst not in self._block_graph[src] or self._block_graph[src][dst] > weight:
                        self._block_graph[src][dst] = weight

        # Compute block centres (mean lat/lon of member nodes)
        for block, nodes in self._block_to_nodes.items():
            lats = [self.coords[n][0] for n in nodes]
            lons = [self.coords[n][1] for n in nodes]
            self._block_centres[block] = (
                sum(lats) / len(lats),
                sum(lons) / len(lons),
            )

    # ------------------------------------------------------------------
    # Heuristic helpers
    # ------------------------------------------------------------------

    @staticmethod
    def great_circle(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Haversine great-circle distance in metres between two geographical points.

        Returns
        -------
        float
            Distance in metres.
        """
        r_earth = 6_371_000.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lam = math.radians(lon2 - lon1)
        a = math.sin(d_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2.0) ** 2
        return r_earth * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    def _node_h(self, node: int, target: int) -> float:
        """Great-circle heuristic between two nodes."""
        lat1, lon1 = self.coords[node]
        lat2, lon2 = self.coords[target]
        return self.great_circle(lat1, lon1, lat2, lon2)

    def _block_h(self, b1: tuple[int, int], b2: tuple[int, int]) -> float:
        """Great-circle heuristic between two block centres."""
        lat1, lon1 = self._block_centres[b1]
        lat2, lon2 = self._block_centres[b2]
        return self.great_circle(lat1, lon1, lat2, lon2)

    # ------------------------------------------------------------------
    # Block-level A*
    # ------------------------------------------------------------------

    def _block_astar(
        self,
        start_block: tuple[int, int],
        end_block: tuple[int, int],
    ) -> list[tuple[int, int]]:
        """
        Run A* on the coarse block graph.

        Returns
        -------
        list[tuple[int, int]]
            Ordered sequence of block indices from *start_block* to *end_block*,
            or an empty list if no path exists.
        """
        if start_block not in self._block_graph and start_block != end_block:
            return []

        g: dict[tuple[int, int], float] = {start_block: 0.0}
        prev: dict[tuple[int, int], tuple[int, int] | None] = {start_block: None}
        h0 = self._block_h(start_block, end_block) if start_block != end_block else 0.0
        heap = MinHeap([(h0, start_block)])
        visited: set[tuple[int, int]] = set()

        while heap.heap:
            _, current = heap.remove()

            if current in visited:
                continue
            visited.add(current)

            if current == end_block:
                # Reconstruct block path
                path: list[tuple[int, int]] = []
                node: tuple[int, int] | None = end_block
                while node is not None:
                    path.append(node)
                    node = prev.get(node)
                path.reverse()
                return path

            for neighbour, weight in self._block_graph.get(current, {}).items():
                if neighbour in visited:
                    continue
                tentative_g = g[current] + weight
                if tentative_g < g.get(neighbour, float("inf")):
                    g[neighbour] = tentative_g
                    prev[neighbour] = current
                    h = self._block_h(neighbour, end_block)
                    heap.insert((tentative_g + h, neighbour))

        return []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def find_shortest_path(
        self,
        start: int,
        end: int,
        padding: int = 1,
        on_visit_callback=None,
    ) -> tuple[float, list[int]]:
        """
        Find the shortest path from *start* to *end* using Block A*.

        The algorithm first identifies the sequence of blocks that the optimal
        path is expected to pass through (block-level A*), then runs a
        node-level A* restricted to those blocks plus *padding* blocks of
        buffer in every cardinal direction.

        Args
        ----
        start : int
            Index of the source node.
        end : int
            Index of the destination node.
        padding : int
            Number of extra blocks added around the block corridor to
            avoid missing near-boundary shortcuts (default 1).
        on_visit_callback : callable, optional
            Called as ``on_visit_callback(visited_set, current_node)`` after
            each node is settled — useful for visualisation.

        Returns
        -------
        tuple[float, list[int]]
            ``(shortest_distance, path)`` where *shortest_distance* is the
            total road distance in metres (or ``inf`` if unreachable) and
            *path* is the ordered list of node indices.
        """
        start_block = self._node_to_block[start]
        end_block = self._node_to_block[end]

        # ---- Step 1: determine the allowed block corridor ----
        if start_block == end_block:
            # Same block – search the whole block plus immediate neighbours
            corridor: set[tuple[int, int]] = set()
            r, c = start_block
            for dr in range(-padding, padding + 1):
                for dc in range(-padding, padding + 1):
                    corridor.add((r + dr, c + dc))
        else:
            block_path = self._block_astar(start_block, end_block)

            if not block_path:
                # No block-level path found; fall back to unrestricted A*
                block_path = [start_block, end_block]

            # Expand each block in the path by *padding* in all directions
            corridor = set()
            for (r, c) in block_path:
                for dr in range(-padding, padding + 1):
                    for dc in range(-padding, padding + 1):
                        corridor.add((r + dr, c + dc))

        # ---- Step 2: node-level A* restricted to the corridor ----
        g_scores = [float("inf")] * self.number_of_vertices
        g_scores[start] = 0.0

        h0 = self._node_h(start, end)
        heap = MinHeap([(h0, start)])
        visited: set[int] = set()
        previous_nodes: list[int | None] = [None] * self.number_of_vertices

        while heap.heap:
            _, vertex = heap.remove()

            if vertex in visited:
                continue
            visited.add(vertex)

            if on_visit_callback is not None:
                on_visit_callback(visited, vertex)

            if vertex == end:
                break

            for edge in self.edges[vertex]:
                destination, weight = edge[0], edge[1]

                if destination in visited:
                    continue

                # Restrict expansion to the block corridor
                if self._node_to_block[destination] not in corridor:
                    continue

                tentative_g = g_scores[vertex] + weight
                if tentative_g < g_scores[destination]:
                    g_scores[destination] = tentative_g
                    previous_nodes[destination] = vertex
                    h = self._node_h(destination, end)
                    heap.insert((tentative_g + h, destination))

        path = self._reconstruct_path(previous_nodes, start, end)
        return g_scores[end], path

    # ------------------------------------------------------------------
    # Path reconstruction
    # ------------------------------------------------------------------

    @staticmethod
    def _reconstruct_path(
        previous_nodes: list[int | None],
        start: int,
        end: int,
    ) -> list[int]:
        """
        Reconstruct the shortest path from *start* to *end* by following
        back-pointers.

        Returns
        -------
        list[int]
            Ordered list of node indices, or an empty list if no path was found.
        """
        path: list[int] = []
        current: int | None = end

        while current is not None:
            path.append(current)
            current = previous_nodes[current]

        path.reverse()

        if not path or path[0] != start:
            return []

        return path
