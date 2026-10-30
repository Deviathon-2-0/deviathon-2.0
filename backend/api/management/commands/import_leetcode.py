from django.core.management.base import BaseCommand
from datasets import load_dataset
from api.models import CatalogQuestion, InterviewQuestion


class Command(BaseCommand):
    help = "Imports LeetCode coding questions from HuggingFace dataset greengerong/leetcode into PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Optional limit on number of questions to import (0 for all 2360).'
        )

    def handle(self, *args, **options):
        limit = options.get('limit', 0)
        self.stdout.write(self.style.NOTICE("Loading HuggingFace dataset 'greengerong/leetcode'..."))
        ds = load_dataset("greengerong/leetcode")
        train_data = ds["train"]
        if limit > 0:
            train_data = train_data.select(range(min(limit, len(train_data))))

        existing_cat = set(CatalogQuestion.objects.values_list('question_key', flat=True))
        existing_iq = set(InterviewQuestion.objects.values_list('source_id', flat=True))

        catalog_records = []
        interview_records = []

        for item in train_data:
            item_id = item.get("id")
            slug = item.get("slug") or f"lc_{item_id}"
            title = item.get("title") or f"Problem {item_id}"
            difficulty = item.get("difficulty") or "Medium"
            if difficulty not in ["Easy", "Medium", "Hard"]:
                difficulty = "Medium"
            content = item.get("content") or ""
            py_solution = item.get("python") or ""
            cpp_solution = item.get("c++") or ""
            java_solution = item.get("java") or ""
            js_solution = item.get("javascript") or ""

            diff_num = 1 if difficulty == "Easy" else (2 if difficulty == "Medium" else 3)
            q_key = f"lc_{slug}"

            if q_key not in existing_cat:
                catalog_records.append(
                    CatalogQuestion(
                        question_key=q_key,
                        title=title,
                        category="Coding",
                        difficulty=difficulty,
                        prompt=content,
                        sample_solution=py_solution,
                        starter_code=f"# Problem: {title} ({difficulty})\n# Write your solution below:\n\n",
                        required_keywords=["time_complexity", "space_complexity", "optimal"],
                        bonus_keywords=["O(1)", "O(n)", "edge_cases"],
                        rubric_breakdown={"definition": 20, "mechanism": 45, "complexity": 20, "edge_cases": 15},
                        child_concept_groups=[]
                    )
                )

            src_id = f"lc_{item_id}_{slug}"
            if src_id not in existing_iq:
                interview_records.append(
                    InterviewQuestion(
                        source_id=src_id,
                        technology="coding",
                        technology_name="Data Structures & Algorithms",
                        difficulty=diff_num,
                        difficulty_label=difficulty,
                        question_type="CODING",
                        prompt=f"{title}\n\n{content}",
                        answer=py_solution,
                        explanation=f"Optimal Solution:\n{py_solution}",
                        tags=["leetcode", slug, difficulty.lower(), "coding"],
                        source_metadata={
                            "leetcode_id": item_id,
                            "slug": slug,
                            "languages": {
                                "python": bool(py_solution),
                                "cpp": bool(cpp_solution),
                                "java": bool(java_solution),
                                "javascript": bool(js_solution)
                            }
                        },
                        is_active=True
                    )
                )

        if catalog_records:
            CatalogQuestion.objects.bulk_create(catalog_records, batch_size=500)
        if interview_records:
            InterviewQuestion.objects.bulk_create(interview_records, batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully synced LeetCode dataset into PostgreSQL!\n"
            f"Total CatalogQuestions: {CatalogQuestion.objects.count()}\n"
            f"Total InterviewQuestions: {InterviewQuestion.objects.count()}"
        ))

