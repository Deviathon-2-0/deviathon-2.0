import os
import sys
from pathlib import Path

backend_dir = Path("backend").resolve()
sys.path.insert(0, str(backend_dir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaira_backend.settings")
import django
django.setup()

from rest_framework.test import APIRequestFactory
from api.views import start_interview_session

factory = APIRequestFactory()

tests = [
    {"track": "Behavioral", "company": "Google", "role": "Engineering Manager"},
    {"track": "System Design", "company": "Amazon", "role": "Senior Systems Architect"},
    {"track": "Tech", "company": "Meta", "role": "Software Engineer"}
]

for t in tests:
    req = factory.post("/api/sessions/start/", t, format="json")
    resp = start_interview_session(req)
    print(f"=== Track: {t['track']} ({t['company']} - {t['role']}) ===")
    for q in resp.data.get("questions", []):
        print(f"  [{q.get('type')}] Q{q.get('index') + 1}: {q.get('title')}")
        print(f"     Prompt preview: {q.get('text')[:80]}...")
        print(f"     Starter Code present: {bool(q.get('starter_code'))}")
