import os
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from rest_framework.test import APIRequestFactory
from api.views import start_interview_session, submit_interview_session, get_session_report, generate_followup_probe
from api.models import InterviewSession, QuestionRecord, FollowUpDialogue
from evaluator.normalizer import PhoneticNormalizer
from evaluator.deterministic_scorer import DeterministicScorer

print("=== 1. Testing Layer 2: Phonetic & Lexicon Normalizer ===")
norm = PhoneticNormalizer()
t1, c1 = norm.normalize("we will be doing wector initialization with demon thread and kaysh memory")
print("Raw:   'we will be doing wector initialization with demon thread and kaysh memory'")
print("Norm:  ", t1)
print("Corrections Count:", len(c1))
assert "vector" in t1, "Failed to normalize wector -> vector"
assert "daemon thread" in t1, "Failed to normalize demon thread -> daemon thread"
assert "cache" in t1, "Failed to normalize kaysh -> cache"
assert "we will do" in t1, "Failed to normalize colloquial syntax"
print("[PASS] Layer 2 Accent Substitution & Metaphone Alignment Verified.")

print("\n=== 2. Testing Layer 1 & Layer 3: Calibrated Scorer & Decoupled Evaluation ===")
scorer = DeterministicScorer()
telemetry_mock = [
    {"timestamp": i * 0.5, "eye_contact": True, "neck_ratio": 1.0, "pitch_hz": 120.0 + (i % 3) * 1.5, "mic_rms": 0.05}
    for i in range(40)
]
# Candidate baseline calibrated during intro
baseline_mock = {"pitch_mean": 121.0, "pitch_std": 12.0, "cadence_sps": 3.3}

eval_res = scorer.evaluate(
    question_id="q_hashmap_internal",
    normalized_transcript="I will use a hashmap with a hash function to calculate bucket index, handle collision using separate chaining with O(1) average lookup time complexity",
    telemetry=telemetry_mock,
    calibrated_baseline=baseline_mock,
    duration_sec=20.0
)
print("Technical Score (Decoupled):", eval_res["technical_score"])
print("Speech Clarity Score:       ", eval_res["acoustic_prosodic_analysis"]["speech_clarity_score"])
print("Modulation Feedback:        ", eval_res["acoustic_prosodic_analysis"]["modulation_feedback"])
print("Cadence Status:             ", eval_res["acoustic_prosodic_analysis"]["cadence_status"])
assert eval_res["technical_score"] >= 70.0, "Technical score should be high for concept-rich response"
assert len(eval_res["acoustic_prosodic_analysis"]["modulation_feedback"]) > 10, "Feedback should be present"
print("[PASS] Layer 1 Acoustic Prosody & Decoupled Evaluation Verified.")

print("\n=== 3. Testing Pre-seeded PostgreSQL Benchmark Sessions ===")
factory = APIRequestFactory()
seeded_ids = [
    ('11111111-2222-3333-4444-555555555551', 'Google SDE-2 (Distributed)'),
    ('22222222-3333-4444-5555-666666666662', 'AWS Systems Architect'),
    ('33333333-4444-5555-6666-777777777773', 'Meta Lead (STAR)')
]
for sid, label in seeded_ids:
    req = factory.get(f'/api/sessions/{sid}/report/')
    resp = get_session_report(req, sid)
    assert resp.status_code == 200, f"Failed to retrieve report for {label}"
    rep = resp.data['report']
    print(f"  [{label}] -> Composite: {rep['compositeScore']}, Tech Score: {rep['scores']['technicalDepth']}, Questions: {len(rep['perQuestionBreakdown'])}")
print("[PASS] All 3 Preloaded Benchmark Sessions Verified in PostgreSQL.")

print("\n=== 4. Testing End-to-End Submission & PostgreSQL Persistence ===")
# Start new session
r_start = factory.post('/api/sessions/start/', {'company': 'Google', 'track': 'Tech', 'round': 'Coding'}, format='json')
res_start = start_interview_session(r_start)
new_sid = res_start.data['session_id']

answers_payload = [
    {
        "question_index": 0,
        "question_text": "Two Sum (Easy)",
        "transcript": "we will do hashmap lookup with O(1) time complexity",
        "code": "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n    return []",
        "followup_prompt": "What is the worst-case space complexity if all elements are distinct?",
        "followup_response": "The worst-case space complexity is O(N) because the hashmap will store all N elements in memory.",
        "duration_sec": 30.0
    }
]
r_sub = factory.post(f'/api/sessions/{new_sid}/submit/', {
    'answers': answers_payload,
    'role': 'Software Engineer',
    'company': 'Google',
    'calibrated_baseline': {'pitch_mean': 122.0, 'pitch_std': 14.0, 'cadence_sps': 3.2}
}, format='json')
res_sub = submit_interview_session(r_sub, new_sid)
assert res_sub.status_code == 200
sub_rep = res_sub.data['report']
print("Live Submission Composite Score:", sub_rep['compositeScore'])
print("Live Technical Depth Score:     ", sub_rep['scores']['technicalDepth'])

# Verify PostgreSQL persistence
q_records = QuestionRecord.objects.filter(session_id=new_sid)
f_dialogues = FollowUpDialogue.objects.filter(session_id=new_sid)
print(f"Database Persisted: {q_records.count()} QuestionRecord(s), {f_dialogues.count()} FollowUpDialogue(s)")
assert q_records.count() >= 1, "Failed to persist QuestionRecord in PostgreSQL"
assert f_dialogues.count() >= 1, "Failed to persist FollowUpDialogue in PostgreSQL"
print("[PASS] End-to-End Interview Engine Execution & PostgreSQL Persistence Verified.")
print("\nAll systems fully calibrated and passing!")
