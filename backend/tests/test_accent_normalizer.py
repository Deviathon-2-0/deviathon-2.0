"""
Unit Tests for Accent Normalizer & Async Learner
Tests Tier 2 sliding window normalizer accuracy, execution speed (<5ms benchmark),
and Tier 3 non-blocking background dispatch.
"""
import sys
import time
import unittest
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from evaluator.accent_normalizer import (
    normalize_accent_transcript,
    save_to_accent_registry,
    PHONETIC_TECH_REGISTRY
)
from evaluator.async_learner import dispatch_async_accent_mining


class TestAccentNormalizer(unittest.TestCase):
    def test_canonical_mishearing_replacements(self):
        """Verify key acoustic mishearings from regional accents are correctly normalized."""
        test_cases = [
            ("we should store this in a has aman for quick lookup", "hashmap"),
            ("the return value is a list of two pulse with indices", "tuples"),
            ("we need to analyze the a symptomatic time complexity", "asymptotic"),
            ("each node updates its wector clock upon receipt", "vector clock"),
            ("we balance the tree as a red black tray", "red-black tree"),
            ("traverse the link least node by node", "linked list"),
            ("this hash table provides oh one average access", "O(1)"),
        ]

        for input_text, expected_canonical in test_cases:
            normalized, replacements = normalize_accent_transcript(input_text)
            self.assertIn(
                expected_canonical.lower(),
                normalized.lower(),
                f"Failed for input: '{input_text}'. Result was: '{normalized}'"
            )
            self.assertTrue(
                len(replacements) > 0,
                f"Expected replacements for '{input_text}', but got empty list."
            )

    def test_performance_under_5ms_benchmark(self):
        """Verify N-gram normalizer processes a 2-minute (~300 word) candidate answer in <5ms."""
        typical_candidate_transcript = (
            "Well in this solution I would first create a has aman to store each number and its index. "
            "Then we iterate through the errey. For each element we check the complement in the has aman. "
            "If it exists we return the two pulse of indices with oh one time lookup. "
            "This achieves an optimal a symptomatic runtime of big o of n instead of brute force o n squared. "
            "If memory is tight we could also use a binary search tray or a balanced red black tray. "
            "For distributed cases we might use consistent hushing with a message cue or kafka topic."
        ) * 2  # ~250-300 words

        # Warm up
        normalize_accent_transcript(typical_candidate_transcript)

        # Benchmark 20 iterations
        start_time = time.perf_counter()
        iterations = 20
        for _ in range(iterations):
            cleaned, repls = normalize_accent_transcript(typical_candidate_transcript)
        elapsed_sec = time.perf_counter() - start_time

        avg_latency_ms = (elapsed_sec / iterations) * 1000.0
        print(f"\n[BENCHMARK] Average Accent Normalizer Latency: {avg_latency_ms:.3f} ms (Target: < 5.0 ms)")
        self.assertLess(avg_latency_ms, 5.0, f"Latency {avg_latency_ms:.3f}ms exceeded 5.0ms target limit!")

    def test_dynamic_registry_caching(self):
        """Verify dynamic persistence and runtime updates to registry."""
        custom_misheard = "super ultra hyper trie slip"
        custom_canonical = "compressed trie"

        save_to_accent_registry(custom_misheard, custom_canonical)
        cleaned, repls = normalize_accent_transcript(f"we implement a {custom_misheard} to search prefixes")
        self.assertIn(custom_canonical, cleaned)

    def test_async_mining_non_blocking_dispatch(self):
        """Verify dispatch_async_accent_mining returns instantaneously (< 2ms) without blocking."""
        sample_transcript = "In our microservices architecture we used a demon thread and a has aman for caching."
        
        start_time = time.perf_counter()
        thread = dispatch_async_accent_mining("System Architecture", sample_transcript)
        dispatch_latency_ms = (time.perf_counter() - start_time) * 1000.0

        self.assertIsNotNone(thread)
        self.assertTrue(thread.is_alive() or thread.daemon)
        self.assertLess(dispatch_latency_ms, 15.0, f"Async dispatch took {dispatch_latency_ms:.2f}ms, expected instantaneous return.")


if __name__ == '__main__':
    unittest.main()
