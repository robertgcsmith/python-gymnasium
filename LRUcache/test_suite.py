import unittest

from LRUcache import LRUCache


class TestLRUCache(unittest.TestCase):
    def test_invalid_capacity(self):
        with self.assertRaises(ValueError):
            LRUCache[str, int](0)
        with self.assertRaises(ValueError):
            LRUCache[str, int](-5)

    def test_capacity_of_one(self):
        cache = LRUCache[str, int](1)
        cache.put("a", 1)
        self.assertEqual(cache.get("a"), 1)
        cache.put("b", 2)  # Should immediately evict "a"
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), 2)

    def test_update_modifies_recency_and_value(self):
        cache = LRUCache[str, int](2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 10)  # Updates value and moves "a" to MRU
        cache.put("c", 3)   # Evicts "b" instead of "a"
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("a"), 10)

    def test_multiple_evictions_and_len(self):
        cache = LRUCache[str, int](2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("d", 4)
        self.assertEqual(len(cache), 2)
        self.assertNotIn("a", cache)
        self.assertNotIn("b", cache)

    def test_comprehensive_repr_and_membership(self) -> None:
        cache = LRUCache[str, int](2)
        cache.put("key1", 100)
        self.assertIn("key1", cache)
        self.assertNotIn("key2", cache)
        expected_repr = "LRUCache(capacity=2, len=1, ordering=MRU->LRU, items={'key1': 100})"
        self.assertEqual(repr(cache), expected_repr)

    def test_get_modifies_recency(self):
        """Verifies that reading a key with get() shifts it to the MRU position."""
        cache = LRUCache[str, int](2)
        cache.put("a", 1)
        cache.put("b", 2)
        
        self.assertEqual(cache.get("a"), 1) # Accessing 'a' makes it MRU
        
        cache.put("c", 3) # Adding 'c' should now evict 'b' instead of 'a'
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("a"), 1)
        self.assertEqual(cache.get("c"), 3)

    def test_cache_miss(self):
        """Ensures looking up non-existent keys returns None safely."""
        cache = LRUCache[str, int](2)
        cache.put("a", 1)
        
        self.assertIsNone(cache.get("b")) # 'b' was never added

    def test_repeated_access_to_same_key(self):
        """Checks that repeatedly hitting the same key doesn't corrupt internal links."""
        cache = LRUCache[str, int](2)
        cache.put("a", 1)
        cache.put("b", 2)
        
        # Continuous reads on the same element
        for _ in range(3):
            self.assertEqual(cache.get("a"), 1)
            
        cache.put("c", 3)  # Should evict 'b'
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("a"), 1)

    def test_membership_does_not_modify_recency(self):
        """Verifies that using 'in' checks presence without altering eviction priority."""
        cache = LRUCache[str, int](2)
        cache.put("a", 1)
        cache.put("b", 2)
        
        # Membership check shouldn't refresh 'a'
        self.assertTrue("a" in cache)
        
        # 'a' is still the LRU item and should be evicted next
        cache.put("c", 3)
        self.assertIsNone(cache.get("a"))
        self.assertIn("b", cache)

    def test_update_with_same_value(self):
        """Ensures putting the exact same value still refreshes its recency."""
        cache = LRUCache[str, int](2)
        cache.put("a", 1)
        cache.put("b", 2)
        
        # Overwrite 'a' with its existing value
        cache.put("a", 1)
        
        # 'b' should be evicted now because 'a' was refreshed
        cache.put("c", 3)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("a"), 1)

    def test_long_sequence_of_operations(self) -> None:
        """Falsification Test: Operational test to stress-test sequence"""
        cache = LRUCache[int, str](3)
        
        # 1. Fill cache completely
        for i in range(1, 4):
            cache.put(i, f"val_{i}")
        
        # 2. Continually access keys to shuffle recency order
        cache.get(1)  # Order: 1 (MRU), 3, 2 (LRU)
        cache.get(2)  # Order: 2 (MRU), 1, 3 (LRU)
        
        # 3. Add an entry that triggers an eviction wave
        cache.put(4, "val_4")  # Should evict 3. Order: 4, 2, 1
        self.assertIsNone(cache.get(3))
        
        # 4. Perform rapid updates and secondary structural additions
        cache.put(1, "updated_1")
        cache.put(5, "val_5")  # Should evict 2. Order: 5, 1, 4
        
        # 5. Final state evaluations
        self.assertIsNone(cache.get(2))
        self.assertEqual(cache.get(1), "updated_1")
        self.assertEqual(cache.get(4), "val_4")
        self.assertEqual(cache.get(5), "val_5")
        self.assertEqual(len(cache), 3)

if __name__ == "__main__":
    unittest.main()


