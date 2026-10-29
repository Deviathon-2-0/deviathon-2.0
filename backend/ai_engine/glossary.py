import re
from difflib import get_close_matches


TECHNICAL_TERMS = [
    "HashMap",
    "HashSet",
    "ArrayList",
    "LinkedList",
    "Binary Search",
    "Dynamic Programming",
    "Recursion",
    "Polymorphism",
    "Encapsulation",
    "Abstraction",
    "Inheritance",
    "Kubernetes",
    "Docker",
    "API",
    "SQL",
    "NoSQL",
    "Python",
    "Java",
    "JavaScript",
    "Machine Learning",
    "Neural Network",
    "Transformer",
    "Database",
    "Operating System",
    "Time Complexity",
    "Space Complexity",
]


def normalize(text):
    """Normalize a term for comparison."""
    return re.sub(r"[^a-z0-9+#]", "", text.lower())


def find_possible_corrections(transcript, glossary=None):
    """
    Suggest possible technical-term corrections.
    The original transcript is never modified.
    """

    if glossary is None:
        glossary = TECHNICAL_TERMS

    words = transcript.split()
    suggestions = []

    normalized_terms = {
        normalize(term): term for term in glossary
    }

    for index, word in enumerate(words):
        normalized_word = normalize(word)

        if not normalized_word:
            continue

        if normalized_word in normalized_terms:
            continue

        matches = get_close_matches(
            normalized_word,
            list(normalized_terms.keys()),
            n=1,
            cutoff=0.80,
        )

        if matches:
            suggestions.append({
                "original": word,
                "suggestion": normalized_terms[matches[0]],
                "confidence": "possible_match",
                "review_required": True,
            })

    # Check adjacent word pairs for terms such as "hash map".
    for index in range(len(words) - 1):
        phrase = f"{words[index]} {words[index + 1]}"
        normalized_phrase = normalize(phrase)

        if normalized_phrase in normalized_terms:
            suggestions.append({
                "original": phrase,
                "suggestion": normalized_terms[normalized_phrase],
                "confidence": "phrase_match",
                "review_required": True,
            })

    return suggestions