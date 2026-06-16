import pytest
from algorithms.dijkstra_heap import DijkstraHeap

@pytest.fixture
def simple_graph():
    """
    Grafo simulado com 4 vértices (0 a 3).
    0 --(1)-- 1
    |         |
   (4)       (2)
    |         |
    2 --(1)-- 3
    
    Caminho mais curto de 0 para 3: 0 -> 1 -> 3 (Custo total: 3)
    """
    return [
        [(1, 1), (2, 4)],       # Arestas saindo do vértice 0
        [(0, 1), (3, 2)],       # Arestas saindo do vértice 1
        [(0, 4), (3, 1)],       # Arestas saindo do vértice 2
        [(1, 2), (2, 1)]        # Arestas saindo do vértice 3
    ]

@pytest.fixture
def disconnected_graph():
    """Grafo onde o vértice 2 é inatingível a partir do 0."""
    return [
        [(1, 5)],      # Vértice 0
        [(0, 5)],      # Vértice 1
        []             # Vértice 2 (Ilhado)
    ]

class TestDijkstra:
    def test_shortest_path_success(self, simple_graph):
        solver = DijkstraHeap(simple_graph)
        distance, path = solver.find_shortest_path(start=0, end=3)
        
        assert distance == 3
        assert path == [0, 1, 3]

    def test_path_to_itself(self, simple_graph):
        solver = DijkstraHeap(simple_graph)
        distance, path = solver.find_shortest_path(start=0, end=0)
        
        assert distance == 0
        assert path == [0]

    def test_unreachable_target(self, disconnected_graph):
        solver = DijkstraHeap(disconnected_graph)
        distance, path = solver.find_shortest_path(start=0, end=2)
        
        # A distância deve ser infinito e o caminho deve estar vazio
        assert distance == float('inf')
        assert path == []

    def test_callback_execution(self, simple_graph):
        solver = DijkstraHeap(simple_graph)
        visited_nodes = []
        
        def mock_callback(visited, current):
            visited_nodes.append(current)
            
        solver.find_shortest_path(start=0, end=3, on_visit_callback=mock_callback)
        
        # O callback deve ter sido chamado, provando que a animação vai funcionar
        assert len(visited_nodes) > 0
        # O alvo final (3) deve ser o último visitado antes do "early exit"
        assert visited_nodes[-1] == 3