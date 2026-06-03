class MinHeap:
    """
    A class that implements a Min-Heap data structure.
    The smallest element is always at the root.
    """

    def __init__(self, array):
        """
        Initializes the MinHeap object and builds the heap in-place.

        Args:
            array: The initial array of elements.
        """
        self.heap = self.build_heap(array)

    def build_heap(self, array):
        """
        Transforms an array into a valid Min-Heap in O(n) time.
        
        Args:
            array: The array to be heapified.
        Returns:
            The heapified array.
        """
        first_parent_idx = (len(array) - 2) // 2
        for current_idx in reversed(range(first_parent_idx + 1)):
            self.sift_down(current_idx, len(array) - 1, array)
        return array

    def sift_down(self, current_idx, end_idx, heap):
        """
        Moves the element at current_idx down the heap until the heap property is restored.

        Args:
            current_idx: The index of the element to sift down.
            end_idx: The last index in the heap.
            heap: The heap array.
        """
        child_one_idx = current_idx * 2 + 1
        while child_one_idx <= end_idx:
            child_two_idx = current_idx * 2 + 2 if current_idx * 2 + 2 <= end_idx else -1
            if child_two_idx != -1 and heap[child_two_idx] < heap[child_one_idx]:
                idx_to_swap = child_two_idx
            else:
                idx_to_swap = child_one_idx

            if heap[idx_to_swap][0] < heap[current_idx][0]: # comparing only distances
                self.swap(current_idx, idx_to_swap, heap)
                current_idx = idx_to_swap
                child_one_idx = current_idx * 2 + 1
            else:
                return

    def sift_up(self, current_idx, heap):
        """
        Moves the element at current_idx up the heap until the heap property is restored.

        Args:
            current_idx: The index of the element to sift up.
            heap: The heap array.
        """
        parent_idx = (current_idx - 1) // 2
        while current_idx > 0 and heap[current_idx][0] < heap[parent_idx][0]: # compating only distances
            self.swap(current_idx, parent_idx, heap)
            current_idx = parent_idx
            parent_idx = (current_idx - 1) // 2

    def peek(self):
        """
        Returns the smallest element in the heap without removing it.

        Returns:
            The root element of the heap.
        """
        return self.heap[0]

    def remove(self):
        """
        Removes and returns the smallest element from the heap.

        Returns:
            The removed element.
        """
        self.swap(0, len(self.heap) - 1, self.heap)
        value_to_remove = self.heap.pop()
        self.sift_down(0, len(self.heap) - 1, self.heap)
        return value_to_remove

    def insert(self, value):
        """
        Inserts a new element into the heap and restores the heap property.

        Args:
            value: The value to be inserted.
        """
        self.heap.append(value)
        self.sift_up(len(self.heap) - 1, self.heap)

    @staticmethod
    def swap(i, j, heap):
        """
        Swaps two elements in the heap.

        Args:
            i: Index of the first element.
            j: Index of the second element.
            heap: The heap array.
        """
        heap[i], heap[j] = heap[j], heap[i]
