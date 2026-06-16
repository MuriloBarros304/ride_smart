import pytest
from algorithms.min_heap import MinHeap

class TestMinHeap:
    def test_build_heap(self):
        # A estrutura armazena tuplas: (distância, vértice)
        initial_array = [(5, 'A'), (3, 'B'), (8, 'C'), (1, 'D'), (2, 'E')]
        heap = MinHeap(initial_array)
        
        # O menor elemento (distância 1) deve estar na raiz
        assert heap.peek() == (1, 'D')

    def test_insert_and_sift_up(self):
        heap = MinHeap([(3, 'A'), (5, 'B')])
        heap.insert((1, 'C'))
        
        # O novo elemento inserido deve subir para a raiz
        assert heap.peek() == (1, 'C')
        assert len(heap.heap) == 3

    def test_remove_and_sift_down(self):
        heap = MinHeap([(1, 'A'), (4, 'B'), (2, 'C'), (6, 'D'), (5, 'E')])
        
        removed = heap.remove()
        assert removed == (1, 'A')
        # O próximo menor (2, 'C') deve assumir a raiz
        assert heap.peek() == (2, 'C')
        assert len(heap.heap) == 4

    def test_empty_heap(self):
        heap = MinHeap([])
        # O Python levanta IndexError ao fazer pop em lista vazia
        with pytest.raises(IndexError):
            heap.remove()