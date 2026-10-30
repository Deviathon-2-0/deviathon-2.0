import os
import sys
import re
from pathlib import Path

# Setup Django environment
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaira_backend.settings")

import django
django.setup()

from datasets import load_dataset
from api.models import CatalogQuestion, InterviewQuestion


def extract_keywords_from_text(title, content):
    """Generates reasonable technical rubric keywords from problem title and text."""
    tech_keywords = [
        "hashmap", "array", "string", "linked_list", "two_pointers", "sliding_window",
        "binary_search", "dynamic_programming", "recursion", "backtracking", "tree",
        "binary_tree", "graph", "bfs", "dfs", "heap", "priority_queue", "stack", "queue",
        "trie", "bit_manipulation", "greedy", "matrix", "prefix_sum", "divide_and_conquer"
    ]
    combined = f"{title} {content}".lower()
    found = [k for k in tech_keywords if k.replace('_', ' ') in combined or k in combined]
    if not found:
        found = ["time_complexity", "space_complexity", "O(n)", "optimal"]
    return found[:6]


def import_leetcode_dataset():
    print("Loading HuggingFace dataset 'greengerong/leetcode'...")
    ds = load_dataset("greengerong/leetcode")
    train_data = ds["train"]
    total_count = len(train_data)
    print(f"Loaded {total_count} LeetCode problems from HuggingFace.")

    catalog_records = []
    interview_records = []
    existing_catalog_keys = set(CatalogQuestion.objects.values_list('question_key', flat=True))
    existing_interview_sources = set(InterviewQuestion.objects.values_list('source_id', flat=True))

    for idx, item in enumerate(train_data):
        item_id = item.get("id")
        slug = item.get("slug") or f"lc_{item_id}"
        title = item.get("title") or f"LeetCode Problem {item_id}"
        difficulty = item.get("difficulty") or "Medium"
        if difficulty not in ["Easy", "Medium", "Hard"]:
            difficulty = "Medium"
        content = item.get("content") or ""
        py_solution = item.get("python") or ""
        cpp_solution = item.get("c++") or ""
        java_solution = item.get("java") or ""
        js_solution = item.get("javascript") or ""

        diff_num = 1 if difficulty == "Easy" else (2 if difficulty == "Medium" else 3)
        keywords = extract_keywords_from_text(title, content)

        # 1. Prepare CatalogQuestion
        q_key = f"lc_{slug}"
        if q_key not in existing_catalog_keys:
            catalog_records.append(
                CatalogQuestion(
                    question_key=q_key,
                    title=title,
                    category="Coding",
                    difficulty=difficulty,
                    prompt=content,
                    sample_solution=py_solution,
                    starter_code=f"# Problem: {title} ({difficulty})\n# Write your solution below:\n\n",
                    required_keywords=keywords,
                    bonus_keywords=["time_complexity", "space_complexity", "O(1)", "edge_cases"],
                    rubric_breakdown={"definition": 20, "mechanism": 45, "complexity": 20, "edge_cases": 15},
                    child_concept_groups=[]
                )
            )

        # 2. Prepare InterviewQuestion
        src_id = f"lc_{item_id}_{slug}"
        if src_id not in existing_interview_sources:
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
                    explanation=f"Optimal Solutions available in Python, C++, Java, and JavaScript.\n\nPython:\n{py_solution}",
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

    print(f"Bulk inserting {len(catalog_records)} new records into CatalogQuestion...")
    if catalog_records:
        CatalogQuestion.objects.bulk_create(catalog_records, batch_size=500)
    print("CatalogQuestion bulk insert complete.")

    print(f"Bulk inserting {len(interview_records)} new records into InterviewQuestion...")
    if interview_records:
        InterviewQuestion.objects.bulk_create(interview_records, batch_size=500)
    print("InterviewQuestion bulk insert complete.")

    total_catalog = CatalogQuestion.objects.count()
    total_interview = InterviewQuestion.objects.count()
    print(f"PostgreSQL Database Totals:")
    print(f"  • CatalogQuestion: {total_catalog} records")
    print(f"  • InterviewQuestion: {total_interview} records")


if __name__ == "__main__":
    import_leetcode_dataset()
