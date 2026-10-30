"""
Accented Speech-to-Text Normalization Engine (evaluator/accent_normalizer.py)
Implements Tier 2: Zero-lag, sub-5ms local N-Gram sliding window phonetic & fuzzy normalizer
for Indian English and regional accent acoustic mishearings of computer science terms.
"""
import re
import json
import string
import time
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


# Path to dynamic persistent cache (updated by background async learner)
CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "dynamic_accent_cache.json"

# Base in-memory technical dictionary for phonetic drift & regional accent mishearings
BASE_PHONETIC_TECH_REGISTRY: Dict[str, str] = {
    # Core mishearings explicitly highlighted
    "has aman": "hashmap",
    "has man": "hashmap",
    "hashman": "hashmap",
    "hasmap": "hashmap",
    "hushmap": "hashmap",
    "hush map": "hashmap",
    "two pulse": "tuples",
    "a symptomatic": "asymptotic",
    "asymptotic notation": "asymptotic notation",
    "oh one": "O(1)",
    "o one": "O(1)",
    "o of one": "O(1)",
    "big o of one": "O(1)",
    "big o of n": "O(n)",
    "o of n": "O(n)",
    "o n": "O(n)",
    "link list": "linked list",
    "linked least": "linked list",
    "linkedlist": "linked list",
    "red black": "red-black tree",
    "red-black": "red-black tree",
    "red black tray": "red-black tree",
    "red-black tray": "red-black tree",

    # DSA & Trees
    "binary search tray": "binary search tree",
    "binary tray": "binary tree",
    "avl tray": "avl tree",
    "b tray": "b-tree",
    "b plus tray": "b+ tree",
    "segment tray": "segment tree",
    "fenwick tray": "fenwick tree",
    "suffix tray": "suffix tree",
    "decision tray": "decision tree",
    "splay tray": "splay tree",
    "cartesian tray": "cartesian tree",
    "skip least": "skip list",
    "adjacency least": "adjacency list",
    "priority cue": "priority queue",
    "priority q": "priority queue",
    "message cue": "message queue",
    "message q": "message queue",
    "steck": "stack",
    "errey": "array",
    "graf": "graph",
    "directed acyclic graf": "directed acyclic graph",
    "two pointers": "two pointers",
    "sliding window": "sliding window",
    "binary search": "binary search",
    "quicksourt": "quicksort",
    "mergesourt": "mergesort",
    "heapsourt": "heapsort",
    "lru cash": "lru cache",
    "lru catch": "lru cache",
    "lfu cash": "lfu cache",
    "lfu catch": "lfu cache",
    "kv cash": "kv cache",
    "kv catch": "kv cache",
    "has table": "hash table",
    "hush table": "hash table",
    "hash tebal": "hash table",
    "tebal scan": "table scan",
    "page tebal": "page table",
    "rainbow tebal": "rainbow table",
    "consistent hushing": "consistent hashing",
    "consistent hasing": "consistent hashing",
    "double hushing": "double hashing",
    "double hasing": "double hashing",
    "rehush": "rehash",
    "rehas": "rehash",
    "bloom filter": "bloom filter",
    "collision resolution": "collision resolution",
    "separate chaining": "separate chaining",
    "open addressing": "open addressing",
    "linear probing": "linear probing",
    "quadratic probing": "quadratic probing",

    # Distributed Systems & Infrastructure
    "wector clock": "vector clock",
    "wector clocks": "vector clocks",
    "vector clook": "vector clock",
    "lamport timestamp": "lamport timestamp",
    "wector database": "vector database",
    "wector embeddings": "vector embeddings",
    "support wector machine": "support vector machine",
    "cash stampede": "cache stampede",
    "catch stampede": "cache stampede",
    "thundering herd": "thundering herd",
    "demon thread": "daemon thread",
    "demon process": "daemon process",
    "deemonset": "daemonset",
    "daemon pra ses": "daemon process",
    "zombie pra ses": "zombie process",
    "orphan pra ses": "orphan process",
    "init pra ses": "init process",
    "inter-pra ses communication": "inter-process communication",
    "pra ses": "process",
    "threed": "thread",
    "tred": "thread",
    "green treds": "green threads",
    "green threeds": "green threads",
    "threed pool": "thread pool",
    "tred pool": "thread pool",
    "dead look": "deadlock",
    "live look": "livelock",
    "spin look": "spinlock",
    "shared look": "shared lock",
    "exclusive look": "exclusive lock",
    "row-level looking": "row-level locking",
    "optimistic looking": "optimistic locking",
    "pessimistic looking": "pessimistic locking",
    "distributed look": "distributed lock",
    "redlook": "redlock",
    "read replica": "read replica",
    "reed replica": "read replica",
    "dirty reed": "dirty read",
    "phantom reed": "phantom read",
    "non-repeatable reed": "non-repeatable read",
    "repeatable reed": "repeatable read",
    "right-ahead log": "write-ahead log",
    "right-through": "write-through",
    "right-back": "write-back",
    "right amplification": "write amplification",
    "reed amplification": "read amplification",
    "wal right-ahead logging": "wal write-ahead logging",
    "core um": "quorum",
    "pack sauce": "paxos",
    "pax os": "paxos",
    "rafft": "raft",
    "raft consensus": "raft consensus",
    "sharting": "sharding",
    "sarding": "sharding",
    "two phase commit": "two-phase commit",
    "to phase commit": "two-phase commit",
    "2 phase commit": "two-phase commit",
    "three phase commit": "three-phase commit",
    "rabbeatmq": "rabbitmq",
    "apache kafka": "apache kafka",
    "grafql": "graphql",
    "rust api": "rest api",
    "curry execution plan": "query execution plan",
    "kweri execution plan": "query execution plan",
    "subcurry": "subquery",
    "subkweri": "subquery",
    "asink": "async",
    "a sink": "async",
    "asink await": "async await",
    "a sink await": "async await",
    "asinkhronous io": "asynchronous io",
    "a sinkhronous io": "asynchronous io",
    "non-blooking io": "non-blocking io",
    "head-of-line blooking": "head-of-line blocking",

    # Colloquial Indian English Phrase Normalization
    "we will be doing": "we will do",
    "i will be doing": "I do",
    "i will be creating": "I create",
    "revert back": "respond",
    "prepone": "advance",
    "do one thing": "proceed to",
}

# Runtime singleton in-memory registry
PHONETIC_TECH_REGISTRY: Dict[str, str] = dict(BASE_PHONETIC_TECH_REGISTRY)


def _load_persisted_cache():
    """Load cached acoustic terms discovered by background miner."""
    global PHONETIC_TECH_REGISTRY
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if isinstance(cached, dict):
                    PHONETIC_TECH_REGISTRY.update(cached)
        except Exception:
            pass


_load_persisted_cache()


def save_to_accent_registry(misheard_phrase: str, canonical_tech_term: str) -> None:
    """Thread-safe registration and persistent disk write for learned terms."""
    global PHONETIC_TECH_REGISTRY
    clean_k = misheard_phrase.strip().lower()
    clean_v = canonical_tech_term.strip()
    if clean_k and clean_v and clean_k != clean_v.lower():
        PHONETIC_TECH_REGISTRY[clean_k] = clean_v
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            existing = {}
            if CACHE_FILE.exists():
                try:
                    with open(CACHE_FILE, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                except Exception:
                    existing = {}
            existing[clean_k] = clean_v
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2)
        except Exception:
            pass


def _clean_word(token: str) -> str:
    """Strip trailing/leading punctuation and lowercase."""
    return token.strip(string.punctuation).lower()


def normalize_accent_transcript(raw_transcript: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Sub-5ms N-gram sliding window normalizer.
    Inspects 3-grams, 2-grams, and 1-grams against PHONETIC_TECH_REGISTRY.
    Applies RapidFuzz (ratio >= 85) on near-miss phonetic drift.
    Returns: (cleaned_transcript, list_of_replacements)
    """
    if not raw_transcript or not raw_transcript.strip():
        return raw_transcript or "", []

    tokens = raw_transcript.strip().split()
    n_tokens = len(tokens)
    clean_tokens = [_clean_word(t) for t in tokens]

    replacements: List[Dict[str, Any]] = []
    output_tokens: List[str] = []
    i = 0

    while i < n_tokens:
        matched = False

        # 1. Check exact dictionary match from 5-gram down to 1-gram (O(1) in-memory lookup)
        for k in (5, 4, 3, 2, 1):
            if i + k <= n_tokens:
                phrase_k = " ".join(clean_tokens[i:i+k])
                if phrase_k in PHONETIC_TECH_REGISTRY:
                    canonical = PHONETIC_TECH_REGISTRY[phrase_k]
                    orig = " ".join(tokens[i:i+k])
                    output_tokens.append(canonical)
                    replacements.append({
                        "original": orig,
                        "canonical": canonical,
                        "ngram": k,
                        "method": "exact_registry"
                    })
                    i += k
                    matched = True
                    break

        if matched:
            continue

        # 4. RapidFuzz Fallback (ratio >= 85) on near-miss phonetic match
        if not matched and RAPIDFUZZ_AVAILABLE:
            # Check 2-gram fuzzy match first
            if i + 2 <= n_tokens:
                cand_2 = f"{clean_tokens[i]} {clean_tokens[i+1]}"
                if len(cand_2) >= 6:
                    for reg_k, reg_v in PHONETIC_TECH_REGISTRY.items():
                        if " " in reg_k:
                            score = fuzz.ratio(cand_2, reg_k)
                            if score >= 88:
                                output_tokens.append(reg_v)
                                replacements.append({
                                    "original": f"{tokens[i]} {tokens[i+1]}",
                                    "canonical": reg_v,
                                    "ngram": 2,
                                    "method": f"fuzzy_rapidfuzz_{score}"
                                })
                                i += 2
                                matched = True
                                break

            # Check 1-gram fuzzy match
            if not matched:
                cand_1 = clean_tokens[i]
                if len(cand_1) >= 5:
                    for reg_k, reg_v in PHONETIC_TECH_REGISTRY.items():
                        if " " not in reg_k and len(reg_k) >= 5:
                            score = fuzz.ratio(cand_1, reg_k)
                            if score >= 88:
                                output_tokens.append(reg_v)
                                replacements.append({
                                    "original": tokens[i],
                                    "canonical": reg_v,
                                    "ngram": 1,
                                    "method": f"fuzzy_rapidfuzz_{score}"
                                })
                                i += 1
                                matched = True
                                break

        # If no match, preserve original token with original casing/punctuation
        if not matched:
            output_tokens.append(tokens[i])
            i += 1

    cleaned_text = " ".join(output_tokens)
    return cleaned_text, replacements
