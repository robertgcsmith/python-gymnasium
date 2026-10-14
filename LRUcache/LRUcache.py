# We need to implement an LRU (Least Recently Used) cache in Python.
# LRU is a cache eviction policy that removes the least recently used items first when the cache reaches capacity.
# Needs to be O(1) for both get and put operations, so we cannot simply use queue/hashmap. This means  O(1) speed, an LRU cache combines two data structures: hash map and doubly linked list.

from typing import Generic, TypeVar

# Define generic type placeholders for Key Type (KT) and Value Type (VT)
KT = TypeVar("KT")
VT = TypeVar("VT")

class BaseNode:
    """A purely structural node containing only pointer connectivity."""
    def __init__(self) -> None:
        self.prev: BaseNode | None = None
        self.next: BaseNode | None = None

class Node(BaseNode, Generic[KT, VT]):
    """A data node that guarantees non-Optional keys and values, removing sentinel leaks."""
    def __init__(self, key: KT, value: VT):
        super().__init__()
        self.key: KT = key
        self.value: VT = value    

class LRUCache(Generic[KT, VT]):
    """
    An LRU Cache combining an amortised O(1) hash map with a doubly linked list.
    
    List Invariant:
    head (sentinel) <-> most recently used ... least recently used <-> tail (sentinel)
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self.capacity: int = capacity
        self.cache: dict[KT, Node[KT, VT]] = {}  # hashmap for O(1) lookup
        self.head: BaseNode = BaseNode()
        self.tail: BaseNode = BaseNode()

        self.head.next = self.tail
        self.tail.prev = self.head

    def _add(self, node: BaseNode) -> None:
          "Add a node right after the head (most recently used position)."
          node.prev = self.head
          node.next = self.head.next
  
          self.head.next.prev = node
          self.head.next = node

    def _remove(self, node: BaseNode) -> None:
        """Remove a node from the doubly linked list, 
        and explicitly encode the invariant. Attached nodes always have neighbors."""
        assert node.prev is not None and node.next is not None
        node.prev.next = node.next
        node.next.prev = node.prev

    def get(self, key:KT) -> VT | None:
        """Return the value if key exists, otherwise return None."""
        node = self.cache.get(key)
        if node is None:
            return None

        self._remove(node)
        self._add(node)
        return node.value

    def put(self, key: KT, value: VT) -> None:
        """Insert or update a key-value pair, evicting the LRU item if over capacity."""
        node = self.cache.get(key)
        if node is not None:
            node.value = value
            self._remove(node)
            self._add(node)
            return
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add(new_node)

        # Eviction logic: If the cache exceeds its capacity, remove the least recently used item (the node just before the tail).
        if len(self.cache) > self.capacity:
            lru_node = self.tail.prev
            assert lru_node is not None and isinstance(lru_node, Node)
            self._remove(lru_node)
            del self.cache[lru_node.key]

    
    def _verify_internal_invariants(self) -> bool:
        """
        Validates internal representation consistency boundaries.
        Returns True if all invariants hold perfectly, otherwise raises an AssertionError.
        """
        visited = set()
        current = self.head
        
        while current is not None:
            if current in visited:
                raise AssertionError("Cycle detected in linked list.")
            visited.add(current)
            
            if current.next is not None and current.next.prev != current:
                    raise AssertionError("Link symmetry violation: forward link disagrees with backward link.")
            
            if current == self.tail:
                break
            current = current.next
        else:
            raise AssertionError("List traversal failed to reach the tail sentinel node.")
            
        real_nodes_count = len(visited) - 2
        if real_nodes_count != len(self.cache):
            raise AssertionError(f"Size mismatch: Linked list has {real_nodes_count} real nodes, but cache has {len(self.cache)}.")
            
        for node in self.cache.values():
            if node not in visited:
                raise AssertionError("Orphan node: A dictionary entry is missing from the linked list.")
                
        return True

    def __contains__(self, key: KT) -> bool:
        "Check if the cache contains a specific key."
        return key in self.cache
    
    def __repr__(self) -> str:
        "Return a string representation of the cache for debugging."
        items = []
        current = self.head.next
        while current != self.tail:
            assert isinstance(current, Node)
            items.append(f"{current.key!r}: {current.value!r}")
            current = current.next
        return f"LRUCache(capacity={self.capacity}, len={len(self.cache)}, ordering=MRU->LRU, items={{{', '.join(items)}}})"

    def __len__(self) -> int:
        "Return the number of items in the cache."
        return len(self.cache)