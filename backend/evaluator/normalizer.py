"""
Phonetic & Lexicon Normalizer (evaluator/normalizer.py)
Normalizes candidate speech transcripts using exact dictionary lookups,
phonetic soundex/metaphone keys, and RapidFuzz token matching to bridge
speech-to-text mishearings (e.g., 'thats why we need has aman' -> 'thats why we need hashmap').
"""
import re
from typing import Dict, List, Tuple, Any, Optional
from evaluator.catalog import PHONETIC_CORRECTIONS

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


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


class PhoneticNormalizer:
    def __init__(self, dictionary: Optional[Dict[str, str]] = None, fuzzy_threshold: float = 85.0):
        self.dictionary: Dict[str, str] = dictionary or PHONETIC_CORRECTIONS
        self.fuzzy_threshold = fuzzy_threshold
        # Pre-sort phrases by word count descending to greedily match longest n-grams first
        self.sorted_phrases = sorted(self.dictionary.keys(), key=lambda p: len(p.split()), reverse=True)
        # Pre-compute phonetic soundex mappings for single-word targets
        self.phonetic_index = {}
        for phrase, target in self.dictionary.items():
            compact = phrase.replace(" ", "")
            sx = compute_soundex(compact)
            if sx and sx not in self.phonetic_index:
                self.phonetic_index[sx] = target

    def normalize(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Normalizes a raw transcript into canonical technical terminology.
        Returns:
            (normalized_text, list of applied corrections with metadata)
        """
        if not text:
            return "", []

        corrections: List[Dict[str, Any]] = []
        normalized = text.strip()

        # Step 1: Direct phrase substitution (Case-insensitive regex boundary match)
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
                        "method": "exact_phrase_match",
                        "start": match.start(),
                        "end": match.end()
                    })
                normalized = pattern.sub(target, normalized)

        # Step 2: N-gram sliding window fuzzy matching (RapidFuzz)
        words = normalized.split()
        if RAPIDFUZZ_AVAILABLE and len(words) > 0:
            modified = False
            for n in [3, 2, 1]:  # Check trigrams, bigrams, unigrams
                i = 0
                while i <= len(words) - n:
                    window = " ".join(words[i:i+n])
                    cleaned_window = re.sub(r'[^\w\s]', '', window).lower()
                    
                    best_match = None
                    best_score = 0.0
                    
                    for phrase in self.sorted_phrases:
                        target = self.dictionary[phrase]
                        # Exact ratio test
                        score = fuzz.ratio(cleaned_window, phrase)
                        if score > best_score and score >= self.fuzzy_threshold:
                            best_score = score
                            best_match = (phrase, target)

                    if best_match and best_match[1] != cleaned_window:
                        matched_phrase, target_term = best_match
                        corrections.append({
                            "original": window,
                            "canonical": target_term,
                            "confidence": round(best_score / 100.0, 2),
                            "method": "fuzzy_ngram_match",
                            "score": best_score
                        })
                        # Replace the slice
                        words = words[:i] + [target_term] + words[i+n:]
                        modified = True
                    else:
                        i += 1
                        
            if modified:
                normalized = " ".join(words)

        # Step 3: Phonetic Soundex check for single word mishearings
        words = normalized.split()
        modified = False
        for idx, word in enumerate(words):
            clean_w = re.sub(r'[^\w]', '', word).lower()
            if len(clean_w) >= 4 and clean_w not in self.dictionary.values():
                sx = compute_soundex(clean_w)
                if sx in self.phonetic_index:
                    target_term = self.phonetic_index[sx]
                    # Verify similarity before replacing to prevent false positives
                    if RAPIDFUZZ_AVAILABLE:
                        ratio = fuzz.ratio(clean_w, target_term.replace("_", ""))
                        if ratio >= 60.0:
                            corrections.append({
                                "original": word,
                                "canonical": target_term,
                                "confidence": 0.85,
                                "method": "soundex_phonetic_match"
                            })
                            words[idx] = target_term
                            modified = True
        if modified:
            normalized = " ".join(words)

        # Clean multiple spaces and formatting
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized, corrections
