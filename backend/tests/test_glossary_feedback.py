import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_engine.glossary import find_possible_corrections
from ai_engine.feedback import generate_feedback


def test_glossary_phrase():
    result = find_possible_corrections(
        "A hash map stores values."
    )

    assert any(
        item["suggestion"] == "HashMap"
        for item in result
    )


def test_feedback_missing_point():
    result = generate_feedback(
        covered_points=["key-value pairs"],
        missing_points=["collision handling"],
        timestamp_seconds=12,
    )

    assert len(result) == 2
    assert result[1]["timestamp_seconds"] == 12
    assert "collision handling" in result[1]["observation"]


if __name__ == "__main__":
    test_glossary_phrase()
    test_feedback_missing_point()

    print("Glossary and feedback tests passed!")