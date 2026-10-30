import os
import sys
import uuid
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imaira_backend.settings')

import django
django.setup()

from api.models import InterviewSession, QuestionRecord

def seed_google_benchmark():
    session_id = uuid.UUID("11111111-2222-3333-4444-555555555551")
    
    # 1. Create or update InterviewSession
    session, created = InterviewSession.objects.get_or_create(id=session_id)
    
    session.role = "Google SDE-2 • Distributed Systems"
    session.company = "Google"
    session.track = "Tech"
    session.seniority_level = "SDE 2"
    session.interviewer_name = "Kabir"
    session.interviewer_accent = "South Indian English (Male)"
    session.coding_language = "python"
    session.status = "completed"
    
    # Quantitative Scores
    session.overall_score = 89.5
    session.score_technical_depth = 91.0
    session.score_structural_logic = 88.5
    session.score_speech_clarity = 90.0
    session.score_body_language = 88.0

    # Human Interviewer Rubric Agreement & Fairness Test Calibration
    session.feedback_summary = {
        "candidateName": "Ravi Kisan",
        "hiringCommitteeDecision": "Strong Hire",
        "humanEvaluatorAgreement": {
            "evaluatorA": 89.0,
            "evaluatorB": 90.0,
            "systemCalibrated": 89.5,
            "parityDelta": "+0.5 pts (Within ±2.0 pt human inter-rater reliability threshold)",
            "fairnessTestStatus": "Passed (Dialect-Neutral Parity Score = 100%)"
        },
        "technicalGlossaryScanned": 2000,
        "accentBiasPenalty": 0.0,
        "privacyStatus": "Zero Audio Retention (Raw audio purged post-scoring; phonetic transcript tokens retained)",
        "strengths": [
            "Demonstrated systematic amortized complexity analysis and concurrent data structures mastery.",
            "Architected a fault-tolerant multi-region rate limiter balancing sub-10ms latency against consistency.",
            "Exemplified high ownership and Googlyness in blameless root-cause mitigation and systemic safeguards."
        ],
        "criticalGaps": [
            "Quantify partition rebalancing latencies and cross-datacenter clock skew failure modes earlier.",
            "State P99.9 tail latencies explicitly during initial architectural requirements gathering."
        ],
        "recommendations": [
            {
                "title": "Distributed Consensus Semantics",
                "description": "Formally contrast Raft log compaction vs Multi-Paxos leader election semantics under asymmetric network partitions."
            },
            {
                "title": "Cache Eviction Bounds",
                "description": "Articulate memory fragmentation overhead in Doubly-Linked-List node allocations and explore flat-array ring buffers."
            }
        ]
    }

    # Concept breakdown for 3 questions
    session.concept_breakdown = [
        {
            "questionIndex": 0,
            "title": "Design LRU Cache with TTL Expiration",
            "category": "Coding / Algorithms",
            "score": 92.0,
            "timeSpent": "9m 14s",
            "status": "Optimal Solution",
            "rawTranscript": "in python we use dict or two pulse for ordering and has aman gives oh one lookup time with dll",
            "normalizedTranscript": "in python we use dict or tuples for ordering and hashmap gives O(1) lookup time with dll",
            "phoneticReplacements": [
                {"misheard": "two pulse", "canonical": "tuples"},
                {"misheard": "has aman", "canonical": "hashmap"},
                {"misheard": "oh one", "canonical": "O(1)"}
            ],
            "rubricCoverage": [
                {"criterion": "Amortized O(1) get and put operations", "status": "Mastered", "weight": 35},
                {"criterion": "TTL timestamp expiration with lazy eviction", "status": "Mastered", "weight": 35},
                {"criterion": "Thread-safe reader-writer locking primitives", "status": "Proficient", "weight": 30}
            ],
            "feedback": "Outstanding algorithmic decomposition. Correctly paired a doubly linked list with a hashmap to guarantee deterministic O(1) eviction."
        },
        {
            "questionIndex": 1,
            "title": "Architect Global Distributed Rate Limiter (500k RPS)",
            "category": "System Design",
            "score": 88.0,
            "timeSpent": "12m 30s",
            "status": "High Scale Architecture",
            "rawTranscript": "we can implement dike stra or token bucket with redis cluster and link list for sliding window to maintain a symptomatic bounds",
            "normalizedTranscript": "we can implement dijkstra or token bucket with redis cluster and linked_list for sliding window to maintain asymptotic bounds",
            "phoneticReplacements": [
                {"misheard": "dike stra", "canonical": "dijkstra"},
                {"misheard": "link list", "canonical": "linked_list"},
                {"misheard": "a symptomatic", "canonical": "asymptotic"}
            ],
            "rubricCoverage": [
                {"criterion": "Token Bucket vs Sliding Window Log Trade-off", "status": "Mastered", "weight": 35},
                {"criterion": "Multi-region Redis cluster with local batching", "status": "Proficient", "weight": 35},
                {"criterion": "Clock skew mitigation and fail-open resilience", "status": "Developing", "weight": 30}
            ],
            "feedback": "Robust distributed topologies. Proposed local in-memory token replenishment with periodic Redis syncing to avoid cross-region network roundtrips."
        },
        {
            "questionIndex": 2,
            "title": "Production Outage Remediation & Blameless Post-Mortem",
            "category": "Behavioral / Leadership (Googlyness)",
            "score": 88.5,
            "timeSpent": "6m 45s",
            "status": "Exceptional Leadership",
            "rawTranscript": "when replication lag spiked we drained traffic immediately and ran a blameless post-mortem to build automated circuit breakers",
            "normalizedTranscript": "when replication lag spiked we drained traffic immediately and ran a blameless post-mortem to build automated circuit breakers",
            "phoneticReplacements": [],
            "rubricCoverage": [
                {"criterion": "Immediate incident containment & user communication", "status": "Mastered", "weight": 40},
                {"criterion": "Blameless RCA & systemic safeguard implementation", "status": "Mastered", "weight": 40},
                {"criterion": "Cross-functional stakeholder alignment", "status": "Proficient", "weight": 20}
            ],
            "feedback": "Exemplified authentic engineering maturity. Focused squarely on improving telemetry alerts and automated degradation rather than assigning personal fault."
        }
    ]

    # Tri-Signal Biometric Integrity Matrix
    session.telemetry_matrix = {
        "integrity_telemetry": {
            "gaze_centered_percentage": 92.4,
            "posture_poise_percentage": 88.0,
            "average_pitch_variance_hz": 21.4,
            "reading_saccades_detected": 0,
            "lip_sync_mismatch_frames": 0,
            "speaking_cadence_wpm": 138,
            "integrity_status": "Verified (Organic)"
        },
        "signal_breakdown": {
            "visual": "92.4% steady webcam gaze with 0 unauthorized saccadic glances.",
            "acoustic": "Dynamic 21.4 Hz vocal inflection with 138 WPM natural delivery.",
            "audio_visual_alignment": "100% In-Sync; zero synthetic audio injection or voice cloning detected."
        }
    }

    session.code_evaluation = {
        "language": "python",
        "syntax_valid": True,
        "test_cases_passed": 5,
        "test_cases_total": 5,
        "time_complexity": "O(1) amortized",
        "space_complexity": "O(N) where N is capacity"
    }

    session.save()

    # 2. Seed QuestionRecords
    QuestionRecord.objects.filter(session=session).delete()
    for q in session.concept_breakdown:
        QuestionRecord.objects.create(
            session=session,
            question_index=q["questionIndex"],
            title=q["title"],
            text=q["title"],
            candidate_transcript=q["normalizedTranscript"],
            score=q["score"],
            expected_concepts=[r["criterion"] for r in q["rubricCoverage"]],
            evaluation_details={
                "raw_transcript": q["rawTranscript"],
                "normalized_transcript": q["normalizedTranscript"],
                "phonetic_replacements": q["phoneticReplacements"],
                "rubric_coverage": q["rubricCoverage"],
                "feedback": q["feedback"]
            }
        )

    print(f"Successfully seeded Google Benchmark Session [{session.id}] for {session.feedback_summary['candidateName']}!")
    print(f"Overall Score: {session.overall_score} ({session.feedback_summary['hiringCommitteeDecision']})")
    print(f"Agreement: Evaluator A={session.feedback_summary['humanEvaluatorAgreement']['evaluatorA']}, Evaluator B={session.feedback_summary['humanEvaluatorAgreement']['evaluatorB']}")

if __name__ == '__main__':
    seed_google_benchmark()
