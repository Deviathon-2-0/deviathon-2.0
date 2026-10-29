def generate_feedback(
    covered_points,
    missing_points,
    timestamp_seconds=0,
):
    """
    Generate actionable feedback from the evaluation results.

    Timestamps must come from actual audio alignment or
    verified annotations. The default timestamp is only a placeholder.
    """

    feedback = []

    for point in covered_points:
        feedback.append({
            "timestamp_seconds": timestamp_seconds,
            "category": "content",
            "observation": f"You covered: {point}.",
            "suggestion": "Keep this explanation in your answer.",
        })

    for point in missing_points:
        feedback.append({
            "timestamp_seconds": timestamp_seconds,
            "category": "content",
            "observation": f"The answer did not cover: {point}.",
            "suggestion": f"Explain {point} and provide an example if appropriate.",
        })

    return feedback