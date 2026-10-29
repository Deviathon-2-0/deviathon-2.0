from ai_engine.evaluation import evaluate_answer
from ai_engine.transcription import transcribe_audio


def evaluate_audio_answer(
    audio_path,
    question,
    expected_points,
):
    """
    Transcribe an interview recording and evaluate its answer.

    Returns the original transcript alongside evaluation results.
    """

    transcription_result = transcribe_audio(
        audio_path=audio_path,
        question=question,
    )

    transcript = transcription_result["transcript"]

    evaluation_result = evaluate_answer(
        answer=transcript,
        expected_points=expected_points,
        question=question,
        use_gemini=True,
    )

    return {
        **evaluation_result,
        "transcription": {
            "model": transcription_result["model"],
            "custom_vocabulary_used": (
                transcription_result["custom_vocabulary_used"]
            ),
        },
    }