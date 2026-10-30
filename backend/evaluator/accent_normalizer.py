"""
Accented Speech-to-Text Normalization Engine (evaluator/accent_normalizer.py)
Implements Tier 2: Zero-lag, sub-5ms local N-Gram sliding window phonetic & fuzzy normalizer
for Indian English and regional accent acoustic mishearings of computer science terms.
Uses RapidFuzz similarity combined with Soundex / Double Metaphone matching (threshold >= 82%).
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

try:
    import jellyfish
    JELLYFISH_AVAILABLE = True
except ImportError:
    JELLYFISH_AVAILABLE = False


# Path to dynamic persistent cache (updated by background async learner)
CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "dynamic_accent_cache.json"

# Common English stopwords skipped during 1-gram fuzzy phonetic replacement
COMMON_STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "as", "into", "through", "over", "after", "between", "under", "about",
    "and", "or", "but", "so", "if", "then", "else", "when", "where", "why",
    "how", "what", "which", "who", "whom", "this", "that", "these", "those",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
    "them", "my", "your", "his", "its", "our", "their", "is", "am", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "shall", "should", "can", "could", "may", "might",
    "must", "well", "first", "then", "iterate", "each", "element", "check",
    "exists", "tight", "cases", "might", "instead", "arrays", "code", "time",
    "bound", "upper", "lower", "loop", "inner", "outer", "index", "return"
}

# Canonical seed lexicon anchoring key CS topics
CANONICAL_SEED_LEXICON: Dict[str, List[str]] = {
    "hashmap": [
        "has aman", "has man", "hash map", "haz a man", "haz man", "hush map", "hushmap",
        "hasmap", "hash tebal", "has table", "hush table", "hashman"
    ],
    "tuples": [
        "two pulse", "two pull", "tuple", "tooples", "two pools", "toopel"
    ],
    "dijkstra": [
        "dike stra", "dike extra", "dyke stra", "dijkstras", "dikestra", "dike stra algorithm",
        "dice tra", "dike star", "dijkstra algorithm"
    ],
    "asymptotic": [
        "a symptomatic", "asymptote", "a symptom", "a symptomatic notation", "asymptotic notation"
    ],
    "O(1)": [
        "oh one", "o one", "o of one", "big o of one", "order of one", "constant time"
    ],
    "O(n)": [
        "oh n", "o n", "o of n", "big o of n", "linear time"
    ],
    "linked list": [
        "link least", "link list", "linked least", "linkedlist", "skip least", "skip list"
    ],
    "vector clock": [
        "wector clock", "wector clok", "wariable clock", "vector clok"
    ],
    "red-black tree": [
        "red black tray", "red black tree", "red-black tray", "red black", "red-black"
    ],
    "priority queue": [
        "priority cue", "priority q", "message cue", "message q"
    ],
    "concurrency": [
        "con currency", "con-currency", "multi tread", "multi treading", "tread safe"
    ],
    "binary search tree": [
        "binary search tray", "binary tray", "bst tray"
    ],
    "consistent hashing": [
        "consistent hushing", "consistent hasing", "double hushing"
    ],
    "lru cache": [
        "lru cash", "lru catch", "lfu cash", "lfu catch"
    ],
}

# Base in-memory technical dictionary for phonetic drift & regional accent mishearings
BASE_PHONETIC_TECH_REGISTRY: Dict[str, str] = {
    # Core mishearings explicitly highlighted
    "has aman": "hashmap",
    "has man": "hashmap",
    "haz a man": "hashmap",
    "haz man": "hashmap",
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
    "dike stra": "dijkstra",
    "dyke stra": "dijkstra",
    "dikestra": "dijkstra",
    "dike extra": "dijkstra",

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

    # Concurrency & OS
    "multi tread": "multithreaded",
    "multi treading": "multithreading",
    "tread pool": "thread pool",
    "tread safe": "thread-safe",
    "tread safety": "thread safety",
    "dead lok": "deadlock",
    "live lok": "livelock",
    "ray condition": "race condition",
    "rays condition": "race condition",
    "mute text": "mutex",
    "mewtex": "mutex",
    "sema four": "semaphore",
    "summer four": "semaphore",
    "spin lok": "spinlock",
    "demon process": "daemon process",
    "demon tread": "daemon thread",
    "demon thread": "daemon thread",
    "fork join": "fork-join",
    "context switch": "context switch",
    "inter process": "inter-process communication",
    "ipc message": "IPC message",
    "shared mem": "shared memory",

    # System Design & Microservices
    "pack sauce": "paxos",
    "pax os": "paxos",
    "raft algorithm": "raft consensus",
    "two face commit": "two-phase commit",
    "three face commit": "three-phase commit",
    "cap tiorem": "CAP theorem",
    "cap tioram": "CAP theorem",
    "acid property": "ACID properties",
    "eventual consistency": "eventual consistency",
    "base property": "BASE properties",
    "lead election": "leader election",
    "split brain": "split-brain scenario",
    "heart bit": "heartbeat signal",
    "gossip protocol": "gossip protocol",
    "circuit breaker": "circuit breaker",
    "rate limiter": "rate limiter",
    "reverse proxi": "reverse proxy",
    "load balancer": "load balancer",
    "round robin": "round robin",
    "sharding key": "sharding key",
    "read replica": "read replica",
    "write ahead log": "write-ahead log",
    "wal file": "WAL file",
    "lsm tray": "LSM-tree",
    "sst tebal": "SSTable",
    "ss table": "SSTable",
    "compaction process": "compaction",

    # Networking & Protocols
    "t c p hand shake": "TCP handshake",
    "three way hand shake": "three-way handshake",
    "syn eck": "SYN-ACK",
    "fin eck": "FIN-ACK",
    "udp packet": "UDP packet",
    "http header": "HTTP header",
    "web socker": "WebSocket",
    "web sock": "WebSocket",
    "rest full api": "RESTful API",
    "graph q l": "GraphQL",
    "g r p c": "gRPC",
    "gee rpc": "gRPC",
    "protobuff": "Protocol Buffers",
    "proto buff": "Protocol Buffers",
    "dns look up": "DNS lookup",
    "b g p router": "BGP router",
    "c d n edge": "CDN edge",
    "t l s certificate": "TLS certificate",
    "ssl hand shake": "SSL handshake",

    # Indian English & Regional Acoustic Slips
    "wector clock": "vector clock",
    "wariable": "variable",
    "wariables": "variables",
    "wirtual memory": "virtual memory",
    "wirtual function": "virtual function",
    "walue": "value",
    "walidation": "validation",
    "wersion control": "version control",
    "asink": "async",
    "a sink": "async",
    "sinkronous": "synchronous",
    "sinkronize": "synchronize",
    "d queue": "deque",
    "d cue": "deque",
    "double ended cue": "double-ended queue",
    "bitwise operation": "bitwise operation",
    "bit manipulation": "bit manipulation",
    "endianness": "endianness",
    "little indian": "little-endian",
    "big indian": "big-endian"
}

# Active in-memory registry
PHONETIC_TECH_REGISTRY: Dict[str, str] = dict(BASE_PHONETIC_TECH_REGISTRY)

# Precomputed phonetic patterns partitioned by word count for sub-5ms performance
PAIRS_BY_WORDCOUNT: Dict[int, List[Dict[str, Any]]] = {1: [], 2: [], 3: [], 4: [], 5: []}


def _compute_phonetic_metadata():
    """Build partitioned lookup table by word count with Soundex and Metaphone signatures."""
    global PAIRS_BY_WORDCOUNT
    PAIRS_BY_WORDCOUNT = {1: [], 2: [], 3: [], 4: [], 5: []}
    
    seen_variants = set()

    # 1. Index Canonical Seed Lexicon
    for canon, variants in CANONICAL_SEED_LEXICON.items():
        for v in variants:
            v_clean = v.lower()
            if v_clean in seen_variants:
                continue
            seen_variants.add(v_clean)

            v_compact = v_clean.replace(" ", "")
            w_count = len(v_clean.split())
            if w_count not in PAIRS_BY_WORDCOUNT:
                PAIRS_BY_WORDCOUNT[w_count] = []

            v_soundex = jellyfish.soundex(v_compact) if (JELLYFISH_AVAILABLE and v_compact.isalnum()) else ""
            v_meta = jellyfish.metaphone(v_compact) if (JELLYFISH_AVAILABLE and v_compact.isalnum()) else ""

            PAIRS_BY_WORDCOUNT[w_count].append({
                "variant": v_clean,
                "compact": v_compact,
                "canonical": canon,
                "soundex": v_soundex,
                "metaphone": v_meta,
                "words_count": w_count
            })

    # 2. Index Registry Variations
    for k, v in PHONETIC_TECH_REGISTRY.items():
        k_clean = k.lower()
        if k_clean in seen_variants:
            continue
        seen_variants.add(k_clean)

        k_compact = k_clean.replace(" ", "")
        w_count = len(k_clean.split())
        if w_count not in PAIRS_BY_WORDCOUNT:
            PAIRS_BY_WORDCOUNT[w_count] = []

        k_soundex = jellyfish.soundex(k_compact) if (JELLYFISH_AVAILABLE and k_compact.isalnum()) else ""
        k_meta = jellyfish.metaphone(k_compact) if (JELLYFISH_AVAILABLE and k_compact.isalnum()) else ""

        PAIRS_BY_WORDCOUNT[w_count].append({
            "variant": k_clean,
            "compact": k_compact,
            "canonical": v,
            "soundex": k_soundex,
            "metaphone": k_meta,
            "words_count": w_count
        })


def load_persistent_cache():
    """Load dynamic persistent cache entries into active registry."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if isinstance(cached, dict):
                    PHONETIC_TECH_REGISTRY.update(cached)
        except Exception:
            pass
    _compute_phonetic_metadata()


# Load cache on import
load_persistent_cache()


def save_to_accent_registry(misheard: str, canonical: str) -> None:
    """Dynamically register newly mined phonetic terms and persist to disk."""
    clean_k = misheard.strip().lower()
    clean_v = canonical.strip()
    if not clean_k or not clean_v:
        return

    PHONETIC_TECH_REGISTRY[clean_k] = clean_v
    
    k_compact = clean_k.replace(" ", "")
    w_count = len(clean_k.split())
    if w_count not in PAIRS_BY_WORDCOUNT:
        PAIRS_BY_WORDCOUNT[w_count] = []

    k_soundex = jellyfish.soundex(k_compact) if (JELLYFISH_AVAILABLE and k_compact.isalnum()) else ""
    k_meta = jellyfish.metaphone(k_compact) if (JELLYFISH_AVAILABLE and k_compact.isalnum()) else ""

    PAIRS_BY_WORDCOUNT[w_count].append({
        "variant": clean_k,
        "compact": k_compact,
        "canonical": clean_v,
        "soundex": k_soundex,
        "metaphone": k_meta,
        "words_count": w_count
    })

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        current_data = {}
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                current_data = json.load(f)
        current_data[clean_k] = clean_v
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=2)
    except Exception:
        pass


def _clean_word(token: str) -> str:
    """Strip trailing/leading punctuation and lowercase."""
    return token.strip(string.punctuation).lower()


def normalize_accent_transcript(raw_transcript: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Sub-5ms N-gram sliding window normalizer combining exact, phonetic (Soundex/Metaphone),
    and RapidFuzz similarity matching (threshold >= 82%).
    Inspects 3-grams, 2-grams, and 1-grams against PHONETIC_TECH_REGISTRY & CANONICAL_SEED_LEXICON.
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

        # Phase 1: Exact dictionary match from 5-gram down to 1-gram (O(1) in-memory lookup)
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

        # Phase 2: Phonetic & Fuzzy Sliding Window (Threshold >= 82%)
        # Strictly checks window k against patterns of length k to prevent boundary word absorption
        for k in (3, 2, 1):
            if i + k <= n_tokens:
                sub_clean = " ".join(clean_tokens[i:i+k])
                
                # Fast path: Skip 1-gram stopwords from fuzzy check
                if k == 1 and (sub_clean in COMMON_STOPWORDS or len(sub_clean) < 4):
                    continue

                sub_compact = "".join(clean_tokens[i:i+k])
                sub_len = len(sub_compact)
                
                sub_soundex = None
                sub_meta = None

                best_match = None
                best_score = 0.0
                best_method = ""

                candidates_pool = PAIRS_BY_WORDCOUNT.get(k, [])
                if not candidates_pool:
                    continue

                for item in candidates_pool:
                    target_len = len(item["compact"])
                    if abs(sub_len - target_len) > 3:
                        continue

                    # Ultra-fast single compact RapidFuzz comparison
                    max_ratio = fuzz.ratio(sub_compact, item["compact"]) if RAPIDFUZZ_AVAILABLE else 0.0

                    if max_ratio < 68.0:
                        continue

                    # Compute Soundex/Metaphone lazily only when text similarity indicates viable candidate
                    if sub_soundex is None:
                        sub_soundex = jellyfish.soundex(sub_compact) if (JELLYFISH_AVAILABLE and sub_compact.isalnum()) else ""
                        sub_meta = jellyfish.metaphone(sub_compact) if (JELLYFISH_AVAILABLE and sub_compact.isalnum()) else ""

                    soundex_match = bool(sub_soundex and sub_soundex == item["soundex"])
                    meta_match = bool(sub_meta and sub_meta == item["metaphone"])

                    if soundex_match and max_ratio >= 72:
                        effective_score = max(max_ratio, 88.0)
                        method_label = "soundex_phonetic_align"
                    elif meta_match and max_ratio >= 72:
                        effective_score = max(max_ratio, 85.0)
                        method_label = "metaphone_phonetic_align"
                    else:
                        effective_score = max_ratio
                        method_label = f"rapidfuzz_ratio_{round(max_ratio, 1)}"

                    if effective_score > best_score:
                        best_score = effective_score
                        best_match = item["canonical"]
                        best_method = method_label
                
                # Apply replacement if similarity meets or exceeds 82% threshold
                if best_match and best_score >= 82.0:
                    orig = " ".join(tokens[i:i+k])
                    output_tokens.append(best_match)
                    replacements.append({
                        "original": orig,
                        "canonical": best_match,
                        "ngram": k,
                        "confidence": round(best_score / 100.0, 2),
                        "method": best_method
                    })
                    i += k
                    matched = True
                    break

        # If no match, preserve original token
        if not matched:
            output_tokens.append(tokens[i])
            i += 1

    cleaned_text = " ".join(output_tokens)
    return cleaned_text, replacements
