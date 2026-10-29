from ai_engine.evaluation import (
    evaluate_content,
    evaluate_structure,
    evaluate_communication
)


expected_points = [
    "key-value pairs",
    "hash function",
    "average-case lookup",
    "collision handling"
]

answer = """
First, a HashMap stores key-value pairs.
It uses a hash function to locate data.
For example, average-case lookup takes O(1) time.
"""


def test_content_score():
    result = evaluate_content(answer, expected_points)

    assert result["score"] == 75
    assert "collision handling" in result["missing_points"]


def test_structure_score():
    score = evaluate_structure(answer)

    assert 0 <= score <= 100


def test_communication_score():
    score = evaluate_communication(answer)

    assert 0 <= score <= 100


if __name__ == "__main__":
    test_content_score()
    test_structure_score()
    test_communication_score()

    print("All evaluation tests passed!")