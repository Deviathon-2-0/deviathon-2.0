"""
Phonetic & Lexicon Normalizer (evaluator/normalizer.py)
Implements Layer 2 (Phonemic & Lexicon Alignment):
- Accent Substitution Matrix (v/w interchange, retroflex consonant drops, vowel shifts)
- Double Metaphone + RapidFuzz Levenshtein phonetic matching (threshold > 0.82)
- Dialect and colloquial phrasing tolerance
- Decoupled technical vocabulary normalization
"""
import re
from typing import Dict, List, Tuple, Any, Optional

try:
    import jellyfish
    JELLYFISH_AVAILABLE = True
except ImportError:
    JELLYFISH_AVAILABLE = False

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

from evaluator.catalog import PHONETIC_CORRECTIONS


# ---------------------------------------------------------------------------
# Accent Substitution Matrix (Acoustic drift across regional dialects)
# ---------------------------------------------------------------------------
ACCENT_SUBSTITUTION_RULES: List[Tuple[re.Pattern, str]] = [
    # 1. /v/ and /w/ interchange (e.g., "wector" -> "vector", "wariable" -> "variable")
    (re.compile(r'\bwector\b', re.IGNORECASE), "vector"),
    (re.compile(r'\bwectors\b', re.IGNORECASE), "vectors"),
    (re.compile(r'\bwariable\b', re.IGNORECASE), "variable"),
    (re.compile(r'\bwariables\b', re.IGNORECASE), "variables"),
    (re.compile(r'\bwirtual\b', re.IGNORECASE), "virtual"),
    (re.compile(r'\bwalue\b', re.IGNORECASE), "value"),
    (re.compile(r'\bwalues\b', re.IGNORECASE), "values"),
    (re.compile(r'\bwalidation\b', re.IGNORECASE), "validation"),

    # 2. Vowel shifts & homophone drift for common tech terms
    (re.compile(r'\b(cashe|kaysh|cash memory|kash)\b', re.IGNORECASE), "cache"),
    (re.compile(r'\bdemon process\b', re.IGNORECASE), "daemon process"),
    (re.compile(r'\bdemon thread\b', re.IGNORECASE), "daemon thread"),
    (re.compile(r'\broute(r)?\b', re.IGNORECASE), "router"),
    (re.compile(r'\bbyt(es)?\b', re.IGNORECASE), "bytes"),

    # 3. Retroflex consonant & consonant cluster drops
    (re.compile(r'\bstuck\b(?=\s+(array|pointer|data|overflow))', re.IGNORECASE), "stack"),
    (re.compile(r'\btread\b(?=\s+(pool|safety|safe|lock))', re.IGNORECASE), "thread"),
    (re.compile(r'\bmulti tread(ed)?\b', re.IGNORECASE), "multithreaded"),
    (re.compile(r'\basink\b', re.IGNORECASE), "async"),
    (re.compile(r'\ba sink\b', re.IGNORECASE), "async"),
    (re.compile(r'\bsinkronous\b', re.IGNORECASE), "synchronous"),
    (re.compile(r'\bque\b', re.IGNORECASE), "queue"),
    (re.compile(r'\bcue\b(?=\s+(message|priority|fifo))', re.IGNORECASE), "queue"),

    # 4. Distributed consensus & infrastructure phonetics
    (re.compile(r'\bpack sauce\b', re.IGNORECASE), "paxos"),
    (re.compile(r'\bpax os\b', re.IGNORECASE), "paxos"),
    (re.compile(r'\brafft\b', re.IGNORECASE), "raft"),
    (re.compile(r'\bcore um\b', re.IGNORECASE), "quorum"),
    (re.compile(r'\bshart(ing)?\b', re.IGNORECASE), "sharding"),
    (re.compile(r'\bsarding\b', re.IGNORECASE), "sharding"),
    (re.compile(r'\btwo phase com(m)?it\b', re.IGNORECASE), "two_phase_commit"),
    (re.compile(r'\b2 phase com(m)?it\b', re.IGNORECASE), "two_phase_commit"),
    (re.compile(r'\bto phase com(m)?it\b', re.IGNORECASE), "two_phase_commit"),

    # 5. Colloquial syntax normalization (Semantic Fairness: never penalize regional phrasing)
    (re.compile(r'\bwe will be doing\b', re.IGNORECASE), "we will do"),
    (re.compile(r'\bi will be creating\b', re.IGNORECASE), "I create"),
    (re.compile(r'\brevert back\b', re.IGNORECASE), "respond"),
    (re.compile(r'\bdo one thing\b', re.IGNORECASE), "proceed to"),
    (re.compile(r'\bprepone\b', re.IGNORECASE), "advance"),
]

# Stopwords that should never be phonetically transformed into technical terms
COMMON_STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "with", "by", "from", "of",
    "is", "are", "was", "were", "be", "been", "being", "do", "does", "did", "doing",
    "will", "would", "shall", "should", "can", "could", "may", "might", "must",
    "we", "i", "you", "he", "she", "it", "they", "this", "that", "these", "those",
    "and", "or", "but", "so", "if", "then", "else", "when", "where", "why", "how",
    "not", "no", "yes", "all", "any", "some", "first", "next", "then", "now", "here"
}

CANONICAL_TECH_DICTIONARY: List[str] = [
    "hashmap", "hashtable", "linked_list", "doubly_linked_list", "binary_search",
    "binary_search_tree", "trie", "heap", "priority_queue", "graph", "vector",
    "dynamic_programming", "memoization", "recursion", "two_pointers", "sliding_window",
    "fast_slow_pointers", "breadth_first_search", "depth_first_search", "topological_sort",
    "time_complexity", "space_complexity", "O(1)", "O(n)", "O(log_n)", "O(n^2)",
    "amortized", "worst_case", "best_case", "in_place", "divide_and_conquer",
    "distributed_systems", "microservices", "load_balancer", "consistent_hashing",
    "database_sharding", "replication", "partitioning", "read_replica",
    "acid_transactions", "cap_theorem", "eventual_consistency", "linearizability",
    "paxos", "raft", "quorum", "two_phase_commit", "write_ahead_log", "lsm_tree",
    "b_tree", "bloom_filter", "redis", "memcached", "message_broker", "kafka",
    "idempotency", "rate_limiter", "token_bucket", "leaky_bucket", "circuit_breaker",
    "cache_stampede", "cache_invalidation", "horizontal_scaling", "vertical_scaling",
    "star_framework", "conflict_resolution", "root_cause_analysis", "post_mortem",
    "customer_obsession", "leadership_principles", "trade_offs"
]


def compute_soundex(token: str) -> str:
    """Computes standard Soundex code for phonetic token comparison."""
    token = re.sub(r'[^a-zA-Z]', '', token).upper()
    if not token:
        return ""
    first_letter = token[0]
    mapping = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }
    digits = [first_letter]
    last_code = mapping.get(first_letter, '0')
    for char in token[1:]:
        code = mapping.get(char, '0')
        if code != '0' and code != last_code:
            digits.append(code)
            last_code = code
        elif code == '0':
            last_code = '0'
        if len(digits) == 4:
            break
    while len(digits) < 4:
        digits.append('0')
    return "".join(digits[:4])


def get_metaphone_code(token: str) -> str:
    """Computes Metaphone code using jellyfish or fallback Soundex."""
    cleaned = re.sub(r'[^a-zA-Z]', '', token).lower()
    if not cleaned:
        return ""
    if JELLYFISH_AVAILABLE:
        try:
            return jellyfish.metaphone(cleaned)
        except Exception:
            pass
    return compute_soundex(cleaned)


class PhoneticNormalizer:
    def __init__(self, dictionary: Optional[Dict[str, str]] = None, fuzzy_threshold: float = 84.0):
        self.dictionary: Dict[str, str] = dictionary or PHONETIC_CORRECTIONS
        self.fuzzy_threshold = fuzzy_threshold
        # Pre-sort phrases by word count descending to greedily match longest n-grams first
        self.sorted_phrases = sorted(self.dictionary.keys(), key=lambda p: len(p.split()), reverse=True)
        
        # Pre-compute phonetic codes for canonical vocabulary
        self.canonical_vocab = list(set(list(self.dictionary.values()) + CANONICAL_TECH_DICTIONARY))
        self.canonical_metaphones = {
            term: get_metaphone_code(term.replace("_", ""))
            for term in self.canonical_vocab
            if get_metaphone_code(term.replace("_", ""))
        }

    def normalize(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Normalizes candidate transcript:
        1. Applies Accent Substitution Matrix (v/w interchange, vowel shifts, colloquialisms).
        2. Applies exact phrase dictionary matching.
        3. Applies Double Metaphone + Fuzzy Levenshtein phonetic alignment (threshold > 0.82).
        Returns:
            (normalized_text, list of applied corrections with metadata)
        """
        if not text:
            return "", []

        corrections: List[Dict[str, Any]] = []
        normalized = text.strip()

        # Step 1: Accent Substitution Matrix
        for pattern, replacement in ACCENT_SUBSTITUTION_RULES:
            if pattern.search(normalized):
                matches = list(pattern.finditer(normalized))
                for match in matches:
                    corrections.append({
                        "original": match.group(0),
                        "canonical": replacement,
                        "confidence": 0.95,
                        "method": "accent_substitution_matrix"
                    })
                normalized = pattern.sub(replacement, normalized)

        # Step 2: Direct phrase substitution (Case-insensitive regex boundary match)
        for phrase in self.sorted_phrases:
            target = self.dictionary[phrase]
            pattern = re.compile(rf'(?<!\w){re.escape(phrase)}(?!\w)', re.IGNORECASE)
            matches = list(pattern.finditer(normalized))
            if matches:
                for match in matches:
                    corrections.append({
                        "original": match.group(0),
                        "canonical": target,
                        "confidence": 1.0,
                        "method": "exact_phrase_match"
                    })
                normalized = pattern.sub(target, normalized)

        # Step 3: Double Metaphone + Fuzzy Levenshtein Sliding Window
        words = normalized.split()
        if len(words) > 0 and (JELLYFISH_AVAILABLE or RAPIDFUZZ_AVAILABLE):
            new_words = []
            i = 0
            while i < len(words):
                matched = False
                raw_token = words[i].lower()
                cleaned_token = re.sub(r'[^a-zA-Z0-9]', '', raw_token)

                # Skip stopwords and short common words from phonetic drift replacement
                if cleaned_token in COMMON_STOPWORDS or len(cleaned_token) < 4:
                    new_words.append(words[i])
                    i += 1
                    continue

                chunk_meta = get_metaphone_code(cleaned_token)
                best_term = None
                best_score = 0.0

                for term, term_meta in self.canonical_metaphones.items():
                    term_clean = term.replace("_", "").lower()
                    if len(term_clean) < 4:
                        continue

                    # 1. Metaphone match
                    meta_match = (chunk_meta == term_meta) and bool(chunk_meta)
                    # 2. Surface similarity check
                    surface_sim = (fuzz.ratio(cleaned_token, term_clean) / 100.0) if RAPIDFUZZ_AVAILABLE else 0.0

                    if meta_match and surface_sim >= 0.65:
                        score = 0.92 + (surface_sim * 0.08)
                    elif meta_match:
                        score = 0.83
                    elif surface_sim >= 0.85:
                        score = surface_sim
                    else:
                        score = 0.0

                    if score > best_score:
                        best_score = score
                        best_term = term

                # If phonetic match exceeds user threshold (> 0.82), substitute
                if best_term and best_score >= (self.fuzzy_threshold / 100.0):
                    clean_best = best_term.replace("_", " ")
                    if clean_best.lower() != raw_token:
                        corrections.append({
                            "original": words[i],
                            "canonical": clean_best,
                            "confidence": round(best_score, 2),
                            "method": "metaphone_fuzzy_alignment"
                        })
                        new_words.append(clean_best)
                        i += 1
                        matched = True

                if not matched:
                    new_words.append(words[i])
                    i += 1

            normalized = " ".join(new_words)

        return normalized, corrections
