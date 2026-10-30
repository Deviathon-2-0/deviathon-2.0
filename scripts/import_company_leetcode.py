import os
import sys
import csv
import re
from pathlib import Path

# Setup Django environment
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaira_backend.settings")

import django
django.setup()

from api.models import CompanyQuestionMapping, CatalogQuestion


def clean_slug_from_link(link: str) -> str:
    """Extracts leetcode problem slug from problem URL."""
    if not link:
        return ""
    clean = link.strip().rstrip('/')
    parts = clean.split('/')
    if len(parts) >= 1:
        return parts[-1].strip().lower()
    return ""


def clean_time_window(filename: str) -> str:
    name = Path(filename).stem
    if "Thirty Days" in name or "30 Days" in name:
        return "Thirty Days"
    elif "Three Months" in name or "3 Months" in name:
        return "Three Months"
    elif "Six Months" in name or "6 Months" in name:
        return "Six Months"
    elif "More Than Six" in name:
        return "More Than Six Months"
    elif "All" in name:
        return "All"
    return name


def import_company_questions():
    repo_dir = Path(__file__).resolve().parent.parent / "data" / "leetcode_companies"
    if not repo_dir.exists():
        print(f"Error: {repo_dir} does not exist.")
        return

    print("Building CatalogQuestion slug lookup cache...")
    catalog_map = {}
    for cq in CatalogQuestion.objects.only('id', 'question_key').iterator():
        key = cq.question_key
        catalog_map[key] = cq
        if key.startswith('lc_'):
            catalog_map[key[3:]] = cq

    print(f"Loaded {len(catalog_map)} question slugs in lookup cache.")

    # Track existing mappings to prevent duplicate insertions
    existing_pairs = set(
        CompanyQuestionMapping.objects.values_list('company_name', 'question_slug', 'time_window')
    )
    print(f"Found {len(existing_pairs)} existing company question mappings.")

    company_dirs = sorted([d for d in repo_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
    print(f"Found {len(company_dirs)} company directories to process.")

    batch = []
    total_inserted = 0

    for c_idx, comp_dir in enumerate(company_dirs):
        comp_name = comp_dir.name
        csv_files = list(comp_dir.glob("*.csv"))

        for csv_file in csv_files:
            time_window = clean_time_window(csv_file.name)
            try:
                with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        title = (row.get('Title') or '').strip()
                        link = (row.get('Link') or '').strip()
                        slug = clean_slug_from_link(link)
                        if not slug and title:
                            slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

                        if not slug:
                            continue

                        pair_key = (comp_name, slug, time_window)
                        if pair_key in existing_pairs:
                            continue
                        existing_pairs.add(pair_key)

                        diff_raw = (row.get('Difficulty') or 'Medium').strip().capitalize()
                        if diff_raw not in ['Easy', 'Medium', 'Hard']:
                            diff_raw = 'Medium'

                        try:
                            freq = float(row.get('Frequency', 0.0) or 0.0)
                        except (ValueError, TypeError):
                            freq = 0.0

                        try:
                            acc_rate = float(row.get('Acceptance Rate', 0.0) or 0.0)
                        except (ValueError, TypeError):
                            acc_rate = 0.0

                        topics_raw = (row.get('Topics') or '').strip()
                        topics = [t.strip() for t in topics_raw.split(',') if t.strip()]

                        cat_q = catalog_map.get(slug) or catalog_map.get(f"lc_{slug}")

                        batch.append(
                            CompanyQuestionMapping(
                                company_name=comp_name,
                                question_slug=slug,
                                title=title or slug.replace('-', ' ').title(),
                                difficulty=diff_raw,
                                frequency=freq,
                                acceptance_rate=acc_rate,
                                time_window=time_window,
                                topics=topics,
                                leetcode_url=link,
                                catalog_question=cat_q
                            )
                        )

                        if len(batch) >= 1000:
                            CompanyQuestionMapping.objects.bulk_create(batch, batch_size=1000)
                            total_inserted += len(batch)
                            batch = []

            except Exception as e:
                print(f"Notice reading {csv_file}: {e}")

        if (c_idx + 1) % 50 == 0 or (c_idx + 1) == len(company_dirs):
            print(f"Processed {c_idx + 1}/{len(company_dirs)} companies... (Inserted {total_inserted + len(batch)} mappings)")

    if batch:
        CompanyQuestionMapping.objects.bulk_create(batch, batch_size=1000)
        total_inserted += len(batch)

    final_total = CompanyQuestionMapping.objects.count()
    linked_catalog_count = CompanyQuestionMapping.objects.filter(catalog_question__isnull=False).count()
    print("==================================================")
    print(f"Import Complete!")
    print(f"Total inserted in this run: {total_inserted}")
    print(f"Total CompanyQuestionMapping in PostgreSQL: {final_total}")
    print(f"Total Mappings linked to full LeetCode problem solutions: {linked_catalog_count}")
    print("==================================================")


if __name__ == "__main__":
    import_company_questions()
