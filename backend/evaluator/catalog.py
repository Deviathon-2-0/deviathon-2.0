"""
In-Memory Technical Catalog & Phonetic Seed Registry (evaluator/catalog.py)
Stores interview questions, required/bonus keywords, speech recognition
mishearing maps, and technical rubric definitions.
"""
from typing import Dict, Any

PHONETIC_CORRECTIONS: Dict[str, str] = {
    # Misheard phrase : Target Canonical Technical Term
    "has aman": "hashmap",
    "hash map": "hashmap",
    "hush map": "hashmap",
    "hash table": "hashmap",
    "has man": "hashmap",
    "hash maps": "hashmap",
    "linked list": "linked_list",
    "link list": "linked_list",
    "linklist": "linked_list",
    "oh one": "O(1)",
    "o one": "O(1)",
    "order of one": "O(1)",
    "o of 1": "O(1)",
    "oh of one": "O(1)",
    "oh n": "O(n)",
    "o n": "O(n)",
    "order of n": "O(n)",
    "o of n": "O(n)",
    "oh of n": "O(n)",
    "oh log n": "O(log_n)",
    "o log n": "O(log_n)",
    "order of log n": "O(log_n)",
    "oh n square": "O(n^2)",
    "o n square": "O(n^2)",
    "order of n squared": "O(n^2)",
    "colision": "collision",
    "collison": "collision",
    "colisions": "collision",
    "collisions": "collision",
    "chaining": "separate_chaining",
    "separate chaining": "separate_chaining",
    "open address": "open_addressing",
    "open addressing": "open_addressing",
    "two pointer": "two_pointers",
    "two pointers": "two_pointers",
    "2 pointer": "two_pointers",
    "2 pointers": "two_pointers",
    "fast slow": "fast_slow",
    "fast and slow": "fast_slow",
    "slow and fast": "fast_slow",
    "tortoise hare": "floyd",
    "tortoise and hare": "floyd",
    "floyds": "floyd",
    "floyd": "floyd",
    "cycle detection": "cycle",
    "detect cycle": "cycle",
    "load factor": "load_factor",
    "hash function": "hash_function",
    "hashing function": "hash_function",
    "hash fn": "hash_function",
    "lru cache": "lru_cache",
    "lru": "lru_cache",
    "least recently used": "lru_cache",
    "doubly linked list": "doubly_linked_list",
    "double linked list": "doubly_linked_list",
    "rate limiter": "rate_limiter",
    "token bucket": "token_bucket",
    "leaky bucket": "leaky_bucket",
    "sliding window": "sliding_window",
    "binary search": "binary_search",
    "bin search": "binary_search",
    "dynamic programming": "dynamic_programming",
    "dynamic programing": "dynamic_programming",
    "dp": "dynamic_programming",
    "memoization": "memoization",
    "memoize": "memoization",
    "breadth first": "bfs",
    "depth first": "dfs",
    "time complexity": "time_complexity",
    "space complexity": "space_complexity",
}

INTERVIEW_QUESTION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "q_hashmap_internal": {
        "id": "q_hashmap_internal",
        "title": "Explain how a Hash Map works internally and its complexity trade-offs.",
        "difficulty": "Medium",
        "required_keywords": ["hashmap", "hash_function", "collision", "O(1)"],
        "bonus_keywords": ["separate_chaining", "open_addressing", "load_factor", "O(n)"],
        "rubric_breakdown": {
            "definition": 25,
            "mechanism": 35,
            "complexity": 20,
            "edge_cases": 20
        },
        "child_concept_groups": [
            {"parent": "hashmap", "children": ["hash_function", "collision"]},
            {"parent": "collision", "children": ["separate_chaining", "open_addressing"]}
        ]
    },
    "q_two_pointer": {
        "id": "q_two_pointer",
        "title": "How would you find a cycle in a singly linked list?",
        "difficulty": "Easy",
        "required_keywords": ["linked_list", "two_pointers", "fast_slow", "cycle"],
        "bonus_keywords": ["floyd", "O(1)_space", "O(n)_time"],
        "rubric_breakdown": {
            "definition": 20,
            "mechanism": 40,
            "complexity": 20,
            "edge_cases": 20
        },
        "child_concept_groups": [
            {"parent": "linked_list", "children": ["cycle", "two_pointers"]},
            {"parent": "two_pointers", "children": ["fast_slow", "floyd"]}
        ]
    },
    "q_lru_cache": {
        "id": "q_lru_cache",
        "title": "Design an LRU (Least Recently Used) Cache with O(1) get and put operations.",
        "difficulty": "Medium",
        "required_keywords": ["lru_cache", "hashmap", "doubly_linked_list", "O(1)"],
        "bonus_keywords": ["eviction", "capacity", "time_complexity", "head_tail_dummies"],
        "rubric_breakdown": {
            "definition": 20,
            "mechanism": 45,
            "complexity": 20,
            "edge_cases": 15
        },
        "child_concept_groups": [
            {"parent": "lru_cache", "children": ["hashmap", "doubly_linked_list"]}
        ]
    },
    "q_rate_limiter": {
        "id": "q_rate_limiter",
        "title": "How would you design a distributed API rate limiter?",
        "difficulty": "Hard",
        "required_keywords": ["rate_limiter", "token_bucket", "sliding_window", "concurrency"],
        "bonus_keywords": ["redis", "leaky_bucket", "distributed_locks", "race_condition"],
        "rubric_breakdown": {
            "definition": 20,
            "mechanism": 40,
            "complexity": 20,
            "edge_cases": 20
        },
        "child_concept_groups": [
            {"parent": "rate_limiter", "children": ["token_bucket", "sliding_window"]}
        ]
    },
    "default_general": {
        "id": "default_general",
        "title": "General Technical Architecture & Algorithmic Problem Solving",
        "difficulty": "Medium",
        "required_keywords": ["time_complexity", "space_complexity", "O(1)", "O(n)"],
        "bonus_keywords": ["edge_cases", "tradeoffs", "optimization", "scalability"],
        "rubric_breakdown": {
            "definition": 25,
            "mechanism": 35,
            "complexity": 25,
            "edge_cases": 15
        },
        "child_concept_groups": []
    }
}

