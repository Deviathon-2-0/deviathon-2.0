import re

from ai_engine.feedback import generate_feedback
from ai_engine.glossary import find_possible_corrections


def evaluate_content(answer, expected_points):
    """Baseline phrase-matching evaluator."""

    if not expected_points:
        return {
            "score": 0,
            "covered_points": [],
            "missing_points": [],
        }

    answer_lower = answer.lower()

    covered_points = [
        point for point in expected_points
        if point.lower() in answer_lower
    ]

    missing_points = [
        point for point in expected_points
        if point.lower() not in answer_lower
    ]

    score = round(
        len(covered_points) / len(expected_points) * 100,
        2,
    )

    return {
        "score": score,
        "covered_points": covered_points,
        "missing_points": missing_points,
    }


def evaluate_structure(answer):
    """Baseline estimate of answer structure."""

    if not answer.strip():
        return 0

    sentences = [
        sentence.strip()
        for sentence in re.split(r"[.!?]+", answer.strip())
        if sentence.strip()
    ]

    score = 40

    if len(sentences) >= 2:
        score += 20

    transition_words = [
        "first", "second", "finally", "because",
        "therefore", "however", "for example",
    ]

    answer_lower = answer.lower()

    if any(word in answer_lower for word in transition_words):
        score += 20

    if len(sentences) >= 3:
        score += 20

    return min(score, 100)


def evaluate_communication(answer):
    """
    Baseline text-based estimate only.
    Does not measure accent, pronunciation, or vocal delivery.
    """

    if not answer.strip():
        return 0

    words = answer.split()

    if len(words) < 5:
        return 30

    score = 60

    average_word_length = sum(
        len(word.strip(".,!?;:")) for word in words
    ) / len(words)

    if average_word_length <= 8:
        score += 15

    sentences = [
        sentence.strip()
        for sentence in re.split(r"[.!?]+", answer.strip())
        if sentence.strip()
    ]

    if 1 <= len(sentences) <= 6:
        score += 15

    if len(words) >= 15:
        score += 10

    return min(score, 100)


def evaluate_answer(
    answer,
    expected_points,
    timestamp_seconds=None,
    question=None,
    use_gemini=True,
):
    """
    Evaluate a transcript with Gemini when possible.

    If Gemini evaluation fails, use the baseline evaluator
    and clearly identify the fallback in the returned result.
    """

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("The answer transcript cannot be empty.")

    if not expected_points:
        raise ValueError("Expected evaluation points cannot be empty.")

    glossary_suggestions = find_possible_corrections(answer)

    if use_gemini and question:
        try:
            from ai_engine.gemini_evaluator import evaluate_with_gemini

            result = evaluate_with_gemini(
                question=question,
                expected_points=expected_points,
                transcript=answer,
            )

            result["glossary_suggestions"] = glossary_suggestions
            result["evaluation_method"] = "gemini"
            result["evaluation_warning"] = None

            return result

        except Exception as error:
            warning = (
                "Gemini evaluation failed; baseline evaluation was used. "
                f"Reason: {type(error).__name__}: {error}"
            )

    else:
        warning = (
            "Gemini evaluation was not requested or no question was provided. "
            "Baseline evaluation was used."
        )

    content_result = evaluate_content(answer, expected_points)

    structure_score = evaluate_structure(answer)
    communication_score = evaluate_communication(answer)

    feedback = generate_feedback(
        covered_points=content_result["covered_points"],
        missing_points=content_result["missing_points"],
        timestamp_seconds=timestamp_seconds,
    )

    return {
        "transcript": answer,
        "scores": {
            "content": content_result["score"],
            "structure": structure_score,
            "communication": communication_score,
        },
        "covered_points": content_result["covered_points"],
        "missing_points": content_result["missing_points"],
        "glossary_suggestions": glossary_suggestions,
        "feedback": feedback,
        "evaluation_method": "baseline",
        "evaluation_warning": warning,
    }
