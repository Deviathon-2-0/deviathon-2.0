import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.models import InterviewQuestion


class Command(BaseCommand):
    help = "Import interview questions from the CodePrep JSON dataset."

    def handle(self, *args, **options):

        # Locate the dataset in the project root.
        dataset_path = (
            Path.cwd() / "data" / "question_bank" / "questions.json"
        )

        if not dataset_path.exists():
            raise CommandError(
                f"Dataset not found: {dataset_path}"
            )

        # Read JSON.
        with dataset_path.open("r", encoding="utf-8") as file:
            dataset = json.load(file)

        questions = dataset.get("questions", [])

        if not questions:
            raise CommandError("No questions found in dataset.")

        # Preserve original dataset attribution.
        metadata = {
            "dataset": dataset.get("name"),
            "version": dataset.get("version"),
            "license": dataset.get("license"),
            "attribution": dataset.get("attribution"),
            "source": dataset.get("source"),
        }

        created_count = 0
        updated_count = 0

        with transaction.atomic():

            for question in questions:

                source_id = question.get("id")

                if not source_id:
                    raise CommandError(
                        "A question is missing its unique ID."
                    )

                _, created = InterviewQuestion.objects.update_or_create(
                    source_id=source_id,

                    defaults={
                        "technology": question.get("technology", ""),
                        "technology_name": question.get(
                            "technologyName", ""
                        ),
                        "difficulty": question.get("difficulty", 0),
                        "difficulty_label": question.get(
                            "difficultyLabel", ""
                        ),
                        "question_type": question.get("type", ""),
                        "prompt": question.get("prompt", ""),
                        "answer": question.get("answer", {}),
                        "explanation": question.get("explanation", ""),
                        "tags": question.get("tags", []),
                        "source_metadata": metadata,
                        "is_active": True,
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "\nQuestion bank import completed!"
            )
        )

        self.stdout.write(f"Total questions: {len(questions)}")
        self.stdout.write(f"New questions: {created_count}")
        self.stdout.write(f"Updated questions: {updated_count}")