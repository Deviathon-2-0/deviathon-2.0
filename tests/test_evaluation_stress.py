from ai_engine.evaluation import evaluate_answer


QUESTION = (
    "Explain how a Java HashMap works and "
    "how it handles collisions."
)

EXPECTED_POINTS = [
    "key-value pairs",
    "hash function",
    "average-case lookup",
    "collision handling",
]


def test_correct_answer():
    answer = """
    A HashMap stores data as key-value pairs.
    It uses a hash function to determine the bucket.
    Its average-case lookup time is O(1).
    When two keys map to the same bucket,
    collisions can be handled using chaining.
    """

    result = evaluate_answer(
        answer=answer,
        expected_points=EXPECTED_POINTS,
        question=QUESTION,
        use_gemini=True,
    )

    print("\nCORRECT ANSWER")
    print("Scores:", result["scores"])
    print("Method:", result["evaluation_method"])
    print("Warning:", result.get("evaluation_warning"))
    if result["evaluation_method"] == "gemini":
      print("Concept analysis:", result.get("concept_analysis", []))
    else:
      print("Missing:", result.get("missing_points", []))

    assert 0 <= result["scores"]["content"] <= 100


def test_incomplete_answer():
    answer = """
    A HashMap stores key-value pairs.
    It uses a hash function to locate data.
    """

    result = evaluate_answer(
        answer=answer,
        expected_points=EXPECTED_POINTS,
        question=QUESTION,
        use_gemini=True,
    )

    print("\nINCOMPLETE ANSWER")
    print("Scores:", result["scores"])
    print("Method:", result["evaluation_method"])
    print("Warning:", result.get("evaluation_warning"))
    if result["evaluation_method"] == "gemini":
      print("Concept analysis:", result.get("concept_analysis", []))
    else:
      print("Missing:", result.get("missing_points", []))

    assert 0 <= result["scores"]["content"] <= 100


def test_incorrect_answer():
    answer = """
    A HashMap automatically sorts all its keys.
    It does not use hashing.
    Its main purpose is to arrange elements
    in alphabetical order.
    """

    result = evaluate_answer(
        answer=answer,
        expected_points=EXPECTED_POINTS,
        question=QUESTION,
        use_gemini=True,
    )

    print("\nINCORRECT ANSWER")
    print("Scores:", result["scores"])
    print("Method:", result["evaluation_method"])
    print("Warning:", result.get("evaluation_warning"))
    if result["evaluation_method"] == "gemini":
      print("Concept analysis:", result.get("concept_analysis", []))
    else:
      print("Missing:", result.get("missing_points", []))

    assert 0 <= result["scores"]["content"] <= 100


def test_irrelevant_answer():
    answer = """
    Java supports inheritance and polymorphism.
    A child class can inherit methods from
    its parent class.
    """

    result = evaluate_answer(
        answer=answer,
        expected_points=EXPECTED_POINTS,
        question=QUESTION,
        use_gemini=True,
    )

    print("\nIRRELEVANT ANSWER")
    print("Scores:", result["scores"])
    print("Method:", result["evaluation_method"])
    print("Warning:", result.get("evaluation_warning"))
    if result["evaluation_method"] == "gemini":
      print("Concept analysis:", result.get("concept_analysis", []))
    else:
      print("Missing:", result.get("missing_points", []))

    assert 0 <= result["scores"]["content"] <= 100


if __name__ == "__main__":
    test_correct_answer()
    test_incomplete_answer()
    test_incorrect_answer()
    test_irrelevant_answer()

    print("\nStress tests completed.")