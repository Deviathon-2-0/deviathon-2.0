from api.models import InterviewQuestion


def get_interview_questions(technology, difficulty=None, count=4):
    """
    Retrieve spoken-interview questions from PostgreSQL.
    Prefer SHORT_ANSWER, then use FLASHCARD as fallback.
    """

    questions = InterviewQuestion.objects.filter(
        is_active=True,
        technology__iexact=technology,
        question_type="SHORT_ANSWER"
    )

    if difficulty is not None:
        questions = questions.filter(difficulty=difficulty)

    selected = list(questions.order_by("?")[:count])

    # Fill remaining slots with flashcards.
    remaining = count - len(selected)

    if remaining > 0:
        flashcards = InterviewQuestion.objects.filter(
            is_active=True,
            technology__iexact=technology,
            question_type="FLASHCARD"
        ).exclude(
            id__in=[q.id for q in selected]
        )

        if difficulty is not None:
            flashcards = flashcards.filter(difficulty=difficulty)

        selected.extend(list(flashcards.order_by("?")[:remaining]))

    return selected