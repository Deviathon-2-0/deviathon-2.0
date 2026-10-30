"""
Unit & Integration Tests for Two-Tier Evaluation Pipeline (tests/test_refactored_engine.py)
Tests:
1. PhoneticNormalizer token matching and mishearing corrections.
2. DeterministicScorer rubric calculations, keyword coverage, and behavioral penalties.
3. TimelineEngine chronological slice and moment tagging.
4. GeminiEvaluationService resilient fallback and synthesis.
5. Django API endpoint POST /api/sessions/evaluate/.
"""
import sys
import os
import unittest
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaira_backend.settings")
import django
django.setup()

from evaluator.normalizer import PhoneticNormalizer
from evaluator.deterministic_scorer import DeterministicScorer
from evaluator.timeline_engine import TimelineEngine
from evaluator.gemini_service import GeminiEvaluationService
from rest_framework.test import APIClient


class TestPhoneticNormalizer(unittest.TestCase):
    def setUp(self):
        self.normalizer = PhoneticNormalizer()

    def test_has_aman_to_hashmap(self):
        raw = "thats why we need has aman"
        normalized, corrs = self.normalizer.normalize(raw)
        self.assertEqual(normalized, "thats why we need hashmap")
        self.assertTrue(any(c["canonical"] == "hashmap" for c in corrs))

    def test_compound_technical_phrases(self):
        raw = "we use linked list with fast and slow pointers and oh one time complexity"
        normalized, corrs = self.normalizer.normalize(raw)
        self.assertIn("linked_list", normalized)
        self.assertIn("fast_slow", normalized)
        self.assertIn("O(1)", normalized)

    def test_collision_and_chaining(self):
        raw = "to resolve colision we apply open address or chaining"
        normalized, _ = self.normalizer.normalize(raw)
        self.assertIn("collision", normalized)
        self.assertIn("open_addressing", normalized)
        self.assertIn("separate_chaining", normalized)


class TestDeterministicScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = DeterministicScorer()

    def test_q_hashmap_high_score_with_depth(self):
        transcript = "A hashmap uses a hash_function to achieve O(1) average lookup. When a collision occurs, separate_chaining or open_addressing resolves it with a load_factor check."
        result = self.scorer.evaluate(
            question_id="q_hashmap_internal",
            normalized_transcript=transcript,
            telemetry=[]
        )
        self.assertGreaterEqual(result["overall_score"], 85.0)
        self.assertIn(result["grade"], ["S", "A"])
        self.assertEqual(len(result["keyword_coverage"]["missed_required"]), 0)
        self.assertGreater(len(result["technical_depth"]["synergies_detected"]), 0)

    def test_q_hashmap_missed_keywords(self):
        transcript = "We store key value pairs in an array."
        result = self.scorer.evaluate(
            question_id="q_hashmap_internal",
            normalized_transcript=transcript,
            telemetry=[]
        )
        self.assertLess(result["overall_score"], 45.0)
        self.assertIn("hashmap", result["keyword_coverage"]["missed_required"])
        self.assertIn("collision", result["keyword_coverage"]["missed_required"])

    def test_behavioral_delivery_penalties(self):
        transcript = "A hashmap uses a hash_function to achieve O(1) average lookup and handles collision."
        # Generate telemetry with:
        # - Eye contact loss > 4.5 seconds
        # - Monotone pitch (std dev < 6.5 Hz)
        # - Posture drop > 20%
        telemetry = []
        for i in range(25):
            t = i * 0.5
            # Gaze lost between 3.0s and 8.0s (5.0s continuous drop)
            eye_contact = not (3.0 <= t <= 8.0)
            pitch = 110.0  # Perfectly flat monotone
            neck_ratio = 1.0 if t < 5.0 else 0.75  # 25% drop
            telemetry.append({
                "timestamp": t,
                "eye_contact": eye_contact,
                "pitch_hz": pitch,
                "neck_ratio": neck_ratio
            })

        result = self.scorer.evaluate(
            question_id="q_hashmap_internal",
            normalized_transcript=transcript,
            telemetry=telemetry
        )
        penalties = result["delivery_penalties"]
        penalty_types = [p["type"] for p in penalties]

        self.assertIn("GAZE_DROP", penalty_types)
        self.assertIn("MONOTONE_PITCH", penalty_types)
        self.assertIn("POSTURE_COLLAPSE", penalty_types)
        self.assertGreater(result["total_penalty_deduction"], 12.0)


class TestTimelineEngine(unittest.TestCase):
    def setUp(self):
        self.timeline_engine = TimelineEngine()
        self.scorer = DeterministicScorer()

    def test_flagged_moments_chronology(self):
        transcript = "We use a hashmap with O(1) complexity."
        telemetry = [
            {"timestamp": 1.0, "eye_contact": True, "neck_ratio": 1.0},
            {"timestamp": 2.0, "eye_contact": False, "neck_ratio": 1.0},
            {"timestamp": 3.0, "eye_contact": False, "neck_ratio": 1.0},
            {"timestamp": 4.0, "eye_contact": False, "neck_ratio": 1.0},
            {"timestamp": 5.0, "eye_contact": False, "neck_ratio": 1.0},
            {"timestamp": 6.0, "eye_contact": False, "neck_ratio": 1.0},
            {"timestamp": 7.0, "eye_contact": True, "neck_ratio": 1.0},
        ]
        det_result = self.scorer.evaluate("q_hashmap_internal", transcript, telemetry)
        moments = self.timeline_engine.analyze_timeline(transcript, telemetry, det_result)

        self.assertGreater(len(moments), 0)
        types = [m["type"] for m in moments]
        self.assertTrue("BLUNDER" in types or "NEEDS_IMPROVEMENT" in types)
        # Check timestamps ordering
        for i in range(len(moments) - 1):
            self.assertLessEqual(moments[i]["timestamp_start"], moments[i + 1]["timestamp_start"])


class TestGeminiEvaluationService(unittest.TestCase):
    def setUp(self):
        self.service = GeminiEvaluationService()

    def test_resilient_fallback_synthesis(self):
        session_data = {
            "question_id": "q_hashmap_internal",
            "transcript": "A hashmap provides O(1) amortized lookup.",
            "normalized_transcript": "A hashmap provides O(1) amortized lookup."
        }
        det_result = {
            "question_id": "q_hashmap_internal",
            "question_title": "Explain how a Hash Map works internally and its complexity trade-offs.",
            "overall_score": 75.0,
            "keyword_coverage": {
                "found_required": ["hashmap", "O(1)"],
                "missed_required": ["collision", "hash_function"]
            },
            "delivery_penalties": []
        }
        moments = []
        result = self.service._deterministic_fallback_synthesis(session_data, det_result, moments)

        self.assertIn("synthesis_tier", result)
        self.assertTrue(len(result["executive_summary"]) > 20)
        self.assertGreater(len(result["targeted_coaching_tips"]), 0)
        self.assertIn("suggested_follow_up", result)


class TestDjangoEvaluateEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_post_evaluate_endpoint(self):
        payload = {
            "question_id": "q_hashmap_internal",
            "transcript": "thats why we need has aman with collision handling and O(1) time complexity",
            "telemetry": [
                {"timestamp": 0.5, "eye_contact": True, "pitch_hz": 125, "neck_ratio": 1.0},
                {"timestamp": 1.5, "eye_contact": True, "pitch_hz": 130, "neck_ratio": 1.0}
            ],
            "role": "Software Engineer",
            "company": "Google"
        }
        response = self.client.post("/api/sessions/evaluate/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("overall_score", data)
        self.assertIn("grade", data)
        self.assertIn("phonetic_corrections_applied", data)
        self.assertIn("normalized_transcript", data)
        self.assertIn("hashmap", data["normalized_transcript"])
        self.assertIn("executive_summary", data)
        self.assertIn("targeted_coaching_tips", data)


if __name__ == "__main__":
    unittest.main()
