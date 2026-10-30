import os
import sys
import json
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaira_backend.settings")

import django
django.setup()

from api.models import Company, Role, CatalogQuestion, CodingTestCase, PhoneticGlossary
from evaluator.catalog import PHONETIC_CORRECTIONS, INTERVIEW_QUESTION_REGISTRY
from evaluator.normalizer import compute_soundex


def seed_companies():
    companies_file = backend_dir / "data" / "companies.json"
    if not companies_file.exists():
        print("companies.json not found, skipping...")
        return
    with open(companies_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    count = 0
    for item in data:
        name = item.get("name")
        if not name:
            continue
        Company.objects.update_or_create(
            name=name,
            defaults={
                "sector": item.get("sector", "Tech"),
                "focus": item.get("focus", ""),
                "subroles": item.get("subroles", [])
            }
        )
        count += 1
    print(f"Seeded {count} companies into PostgreSQL.")


def seed_roles():
    roles_file = backend_dir / "data" / "roles.json"
    if not roles_file.exists():
        print("roles.json not found, skipping...")
        return
    with open(roles_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for item in data:
        title = item.get("title")
        if not title:
            continue
        Role.objects.update_or_create(
            title=title,
            defaults={
                "category": item.get("category", "Tech"),
                "focus": item.get("focus", ""),
                "levels": item.get("levels", [])
            }
        )
        count += 1
    print(f"Seeded {count} roles into PostgreSQL.")


def seed_phonetic_glossary():
    count = 0
    for misheard, canonical in PHONETIC_CORRECTIONS.items():
        PhoneticGlossary.objects.update_or_create(
            misheard_token=misheard.lower().strip(),
            defaults={
                "canonical_token": canonical.strip(),
                "soundex_code": compute_soundex(canonical.strip()),
                "category": "technical_term"
            }
        )
        count += 1

    # Also check glossary_test_fixture.json
    fixture_path = backend_dir / "data" / "glossary_test_fixture.json"
    if fixture_path.exists():
        with open(fixture_path, "r", encoding="utf-8") as f:
            fixture_data = json.load(f)
        for term, details in fixture_data.items():
            if isinstance(details, dict):
                alts = details.get("accepted_variants", []) + details.get("common_stt_errors", [])
                for alt in alts:
                    PhoneticGlossary.objects.update_or_create(
                        misheard_token=alt.lower().strip(),
                        defaults={
                            "canonical_token": term.strip(),
                            "soundex_code": compute_soundex(term.strip()),
                            "category": details.get("category", "technical_term")
                        }
                    )
                    count += 1
    print(f"Seeded {count} phonetic glossary entries into PostgreSQL.")


def seed_catalog_questions():
    count = 0
    for q_key, q_data in INTERVIEW_QUESTION_REGISTRY.items():
        cat_q, _ = CatalogQuestion.objects.update_or_create(
            question_key=q_key,
            defaults={
                "title": q_data.get("title", ""),
                "category": "System Design" if (q_key.startswith("sd_") or q_key in ["q_rate_limiter"] or "rate limiter" in q_data.get("title", "").lower() or "system design" in q_data.get("title", "").lower()) else "Coding",
                "difficulty": q_data.get("difficulty", "Medium"),
                "prompt": q_data.get("title", ""),
                "required_keywords": q_data.get("required_keywords", []),
                "bonus_keywords": q_data.get("bonus_keywords", []),
                "rubric_breakdown": q_data.get("rubric_breakdown", {}),
                "child_concept_groups": q_data.get("child_concept_groups", [])
            }
        )
        count += 1

    # Add coding test cases for standard questions
    lru_q = CatalogQuestion.objects.filter(question_key="q_lru_cache").first()
    if lru_q:
        CodingTestCase.objects.update_or_create(
            question=lru_q,
            input_data='["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]\n[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]',
            defaults={
                "expected_output": "[null, null, null, 1, null, -1, null, -1, 3, 4]",
                "is_hidden": False,
                "timeout_seconds": 2.0
            }
        )

    two_pointer_q = CatalogQuestion.objects.filter(question_key="q_two_pointer").first()
    if two_pointer_q:
        CodingTestCase.objects.update_or_create(
            question=two_pointer_q,
            input_data="head = [3,2,0,-4], pos = 1",
            defaults={
                "expected_output": "true",
                "is_hidden": False,
                "timeout_seconds": 1.0
            }
        )

    print(f"Seeded {count} catalog questions & test cases into PostgreSQL.")


if __name__ == "__main__":
    print("Beginning PostgreSQL seed process...")
    seed_companies()
    seed_roles()
    seed_phonetic_glossary()
    seed_catalog_questions()
    print("PostgreSQL seed process complete!")

