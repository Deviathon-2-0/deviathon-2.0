"""
Seed Mock Interview Sessions into PostgreSQL (scripts/seed_mock_sessions.py)
Creates 3 authentic, production-grade mock sessions with full:
- Multi-question breakdown
- Exact timestamps & time scripts (e.g. 00:00 - 01:45)
- Follow-up probes & responses
- Calibrated acoustic prosody (pitch baseline, syllables/sec, pause analysis)
- Candidate performance & integrity matrix
- Decoupled scoring
"""
import os
import sys
import uuid
import datetime

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from api.models import InterviewSession, QuestionRecord, FollowUpDialogue


def seed_mock_results():
    print("Seeding authentic mock interview sessions into PostgreSQL...")

    # =========================================================================
    # Session 1: Google SDE-2 (Distributed Systems & Autocomplete Trie)
    # =========================================================================
    s1_id = uuid.UUID('11111111-2222-3333-4444-555555555551')
    InterviewSession.objects.filter(id=s1_id).delete()

    s1 = InterviewSession.objects.create(
        id=s1_id,
        role="Software Engineer (SDE 2)",
        company="Google",
        track="Tech",
        seniority_level="SDE 2",
        interviewer_name="Kabir",
        interviewer_accent="IN English (Calibrated)",
        coding_language="cpp",
        status="completed",
        overall_score=88.5,
        score_technical_depth=92.0,
        score_structural_logic=88.0,
        score_speech_clarity=85.0,
        score_body_language=86.0,
        feedback_summary={
            "criticalGaps": [
                "Detail memory fragmentation bounds when storing large Top-K autocomplete lists in in-memory Trie nodes.",
                "Quantify cross-datacenter commit wait time variation under asymmetric WAN jitter in Spanner."
            ],
            "recommendations": [
                {"title": "Memory Optimization", "description": "Consider Radix Tree path compression to reduce Trie node pointer overhead in sparse graphs."},
                {"title": "Consensus Resilience", "description": "Discuss leader election pre-vote protocol to prevent isolated partition reconnections from perturbing healthy quorum."},
                {"title": "Conversational Composure", "description": "Your natural syllable-timed cadence maintained steady composure; continue pausing deliberately before architectural trade-offs."}
            ],
            "strengths": [
                "Precise mathematical formulation of O(P) prefix lookup bounds using Trie with cached min-heaps.",
                "Thorough comprehension of TrueTime commit-wait rules and atomic clock drift boundaries in distributed consensus.",
                "Excellent cross-modal delivery with consistent forward engagement and zero scripted tells."
            ]
        },
        concept_breakdown=[
            {
                "question_index": 0,
                "question_title": "Trie-Based Autocomplete Prefix Engine with Top-K Caching",
                "timestamp_start": 0.0,
                "timestamp_end": 105.0,
                "duration_formatted": "00:00 - 01:45",
                "score": 94,
                "transcript": "To optimize autocomplete query latency to sub-millisecond, I will implement a Prefix Trie where each TrieNode maintains a pre-computed Top-K frequency list. Instead of performing a costly DFS traversal on every keystroke, the lookup simply walks down the prefix P in O(P) time and returns the pre-cached suggestions directly.",
                "code": "#include <iostream>\n#include <string>\n#include <vector>\n#include <unordered_map>\n\nstruct TrieNode {\n    bool is_word = false;\n    int frequency = 0;\n    std::unordered_map<char, TrieNode*> children;\n    std::vector<std::string> top_k_cached;\n};\n\nclass AutocompleteEngine {\n    TrieNode* root = new TrieNode();\npublic:\n    std::vector<std::string> searchPrefix(const std::string& prefix) {\n        TrieNode* curr = root;\n        for (char c : prefix) {\n            if (!curr->children.count(c)) return {};\n            curr = curr->children[c];\n        }\n        return curr->top_k_cached;\n    }\n};",
                "followup_prompt": "What is the memory trade-off of maintaining Top-K frequencies at every node versus traversing at query time, and how would you optimize memory under heavy write loads?",
                "followup_response": "Caching Top-K at every node increases memory by O(K * P). In high-volume systems, we can compress non-branching paths using Radix Tree compression and update frequencies asynchronously via a Kafka write-ahead pipeline.",
                "covered_concepts": [
                    {"concept": "Trie Structure", "evidence": "Implemented TrieNode with hashmap children"},
                    {"concept": "O(P) Prefix Complexity", "evidence": "Articulated O(P) traversal bound"},
                    {"concept": "Top-K Caching", "evidence": "Pre-computed cached completions at each node"}
                ],
                "missing_concepts": [],
                "feedback": "Exemplary algorithmic decomposition. Stated the exact asymptotic time bounds upfront and addressed the follow-up memory trade-off effectively."
            },
            {
                "question_index": 1,
                "question_title": "Google Spanner External Consistency & TrueTime Consensus",
                "timestamp_start": 105.0,
                "timestamp_end": 210.0,
                "duration_formatted": "01:45 - 03:30",
                "score": 90,
                "transcript": "Google Spanner guarantees strict external consistency across distributed regions using the TrueTime API, which bounds clock uncertainty epsilon to under 7 milliseconds via synchronized atomic clocks and GPS receivers. Spanner uses 2-Phase Locking for serializability and Paxos state machines for replication.",
                "code": "# Architecture Blueprint:\n# 1. TrueTime API -> [t.earliest, t.latest] where latest - earliest <= 2*epsilon\n# 2. Commit Wait Rule: Pick commit timestamp s >= t.now().latest; wait to release locks until t.now().earliest > s\n# 3. Paxos Leader Lease -> guarantees leader cannot step down while uncertainty interval is pending.",
                "followup_prompt": "Under a cross-datacenter fiber cut where clock drift increases beyond epsilon, how does the system maintain linearizability?",
                "followup_response": "The leader lengthens the commit wait duration to match the expanded uncertainty interval [t.earliest, t.latest]. Throughput decreases, but consistency invariants are never violated.",
                "covered_concepts": [
                    {"concept": "TrueTime API", "evidence": "Articulated bounded clock uncertainty interval"},
                    {"concept": "Commit Wait Rule", "evidence": "Detailing lock release guarantee s < t.now().earliest"},
                    {"concept": "Paxos Consensus", "evidence": "State machine replication with leader leases"}
                ],
                "missing_concepts": [],
                "feedback": "Deep command of distributed consensus mechanics. Accurately explained the commit wait invariant without hesitation."
            }
        ],
        telemetry_matrix={
            "integrity_telemetry": {
                "gaze_centered_percentage": 91,
                "posture_poise_percentage": 88,
                "average_pitch_variance_hz": 14.8,
                "reading_saccades_detected": 0,
                "lip_sync_mismatch_frames": 0,
                "integrity_status": "Verified (Organic)"
            },
            "calibrated_baseline": {
                "pitch_mean": 122.4,
                "pitch_std": 14.8,
                "cadence_sps": 3.4
            }
        }
    )

    # Question Records
    QuestionRecord.objects.filter(session=s1).delete()
    for q_data in s1.concept_breakdown:
        QuestionRecord.objects.create(
            session=s1,
            question_index=q_data["question_index"],
            title=q_data["question_title"],
            text=q_data["transcript"],
            starter_code=q_data.get("code", ""),
            candidate_code=q_data.get("code", ""),
            candidate_transcript=q_data["transcript"],
            score=q_data["score"],
            evaluation_details={"covered": q_data["covered_concepts"], "feedback": q_data["feedback"]}
        )

    # Follow-Up Dialogues
    FollowUpDialogue.objects.filter(session=s1).delete()
    for q_data in s1.concept_breakdown:
        if q_data.get("followup_prompt"):
            FollowUpDialogue.objects.create(
                session=s1,
                question_index=q_data["question_index"],
                candidate_initial_answer=q_data["transcript"],
                probe_type="architecture_tradeoff",
                ai_followup_prompt=q_data["followup_prompt"],
                candidate_followup_answer=q_data.get("followup_response", "")
            )

    print(f"  [Created] Session 1: {s1.id} (Google SDE-2 • Composite {s1.overall_score})")

    # =========================================================================
    # Session 2: Amazon Senior Systems Architect (System Design & Scale)
    # =========================================================================
    s2_id = uuid.UUID('22222222-3333-4444-5555-666666666662')
    InterviewSession.objects.filter(id=s2_id).delete()

    s2 = InterviewSession.objects.create(
        id=s2_id,
        role="Senior Systems Architect",
        company="Amazon Web Services",
        track="System Design",
        seniority_level="Senior SDE",
        interviewer_name="Charlotte",
        interviewer_accent="UK English (Received)",
        coding_language="python",
        status="completed",
        overall_score=84.5,
        score_technical_depth=86.0,
        score_structural_logic=85.0,
        score_speech_clarity=82.0,
        score_body_language=83.0,
        feedback_summary={
            "criticalGaps": [
                "Quantify partition rebalancing latencies in failure recovery modes.",
                "Detail hot-partition throttling mitigations under skewed Prime Day write surges."
            ],
            "recommendations": [
                {"title": "Partition Mitigation", "description": "Incorporate adaptive capacity sharding and write-sharding suffixes for hot items."},
                {"title": "Cache Invalidation", "description": "Contrast lease-based Redis cache invalidation against broadcast pub-sub to mitigate cache stampedes."},
                {"title": "Pacing & Modulation", "description": "Good conversational flow calibrated to your natural cadence. Maintain direct webcam eye contact when contrasting trade-offs."}
            ],
            "strengths": [
                "Structured back-of-the-envelope capacity estimations with explicit QPS and storage growth figures.",
                "Clear separation between Key Generation Service (KGS) and the persistence layer.",
                "Natural cognitive pauses before contrasting write-heavy vs read-heavy database architectures."
            ]
        },
        concept_breakdown=[
            {
                "question_index": 0,
                "question_title": "Design Distributed Pastebin & Scaled URL Shortener",
                "timestamp_start": 0.0,
                "timestamp_end": 120.0,
                "duration_formatted": "00:00 - 02:00",
                "score": 86,
                "transcript": "We estimate 100M daily active writes, translating to ~1,160 writes per second and 11,600 reads per second with a 10:1 read/write ratio. For 5-year storage at 500 bytes per URL, we require approximately 91 Terabytes. We use a standalone Key Generation Service (KGS) cluster that pre-generates 7-character base-62 hash keys.",
                "code": "# Capacity & Architecture:\n# Daily Writes = 100,000,000 / 86400 = ~1,160 writes/sec\n# Daily Reads = 11,600 reads/sec\n# Storage (5 years) = 100M * 365 * 5 * 500B = ~91.2 TB\n# Key Space = 62^7 = ~3.5 Trillion unique strings\n# Persistence: DynamoDB + Redis Cluster with LRU Eviction",
                "followup_prompt": "How do you guarantee that two concurrent KGS workers never issue the same pre-generated key during network failover?",
                "followup_response": "The KGS cluster loads key ranges into memory and marks them as assigned in persistent storage using atomic CAS (compare-and-swap). If a node crashes, its unissued in-memory keys are discarded rather than reused.",
                "covered_concepts": [
                    {"concept": "Capacity Estimation", "evidence": "Detailed QPS and 5-year storage bounds"},
                    {"concept": "Key Generation Service", "evidence": "Pre-allocated base-62 cluster"},
                    {"concept": "Atomic CAS", "evidence": "Guaranteed collision-free key distribution"}
                ],
                "missing_concepts": [],
                "feedback": "Strong back-of-the-envelope math. Solved concurrent key allocation without deadlocks."
            },
            {
                "question_index": 1,
                "question_title": "Design Scalable Web Crawler with Distributed Bloom Filters",
                "timestamp_start": 120.0,
                "timestamp_end": 235.0,
                "duration_formatted": "02:00 - 03:55",
                "score": 83,
                "transcript": "The distributed web crawler needs to index 10 billion pages monthly. The URL Frontier utilizes dual-tier queues: priority queues for page importance ranking and politeness queues mapped to individual domain hostnames to respect robots.txt. Distributed Bloom filters eliminate duplicate crawl requests with sub-1% false positive rates.",
                "code": "# URL Frontier Architecture:\n# 1. URL Filter & Normalizer -> Canonical URL hash\n# 2. Distributed In-Memory Bloom Filter (Redis Cluster)\n# 3. Priority Queues (FIFO by PageRank / Score)\n# 4. Politeness Queues (Mapped to Domain Hostname, Rate Limited)\n# 5. Worker Fleet with DNS Cache to prevent redundant lookups",
                "followup_prompt": "What happens when the Bloom filter reaches memory saturation or exceeds its planned false positive threshold?",
                "followup_response": "We implement a Scalable Bloom Filter or Layered Bloom Filter where new filter layers are dynamically allocated as capacity exceeds 70%, with older layers compacted or snapshotted to disk.",
                "covered_concepts": [
                    {"concept": "URL Frontier", "evidence": "Separated priority from politeness queues"},
                    {"concept": "Bloom Filter", "evidence": "Deduplicated 10 billion URL crawl space"},
                    {"concept": "DNS Caching", "evidence": "Mitigated external nameserver throttling"}
                ],
                "missing_concepts": [],
                "feedback": "Structured distributed architecture. Addressed Bloom filter saturation cleanly."
            }
        ],
        telemetry_matrix={
            "integrity_telemetry": {
                "gaze_centered_percentage": 88,
                "posture_poise_percentage": 86,
                "average_pitch_variance_hz": 13.6,
                "reading_saccades_detected": 0,
                "lip_sync_mismatch_frames": 0,
                "integrity_status": "Verified (Organic)"
            },
            "calibrated_baseline": {
                "pitch_mean": 115.0,
                "pitch_std": 13.6,
                "cadence_sps": 3.1
            }
        }
    )

    QuestionRecord.objects.filter(session=s2).delete()
    for q_data in s2.concept_breakdown:
        QuestionRecord.objects.create(
            session=s2,
            question_index=q_data["question_index"],
            title=q_data["question_title"],
            text=q_data["transcript"],
            starter_code=q_data.get("code", ""),
            candidate_code=q_data.get("code", ""),
            candidate_transcript=q_data["transcript"],
            score=q_data["score"],
            evaluation_details={"covered": q_data["covered_concepts"], "feedback": q_data["feedback"]}
        )

    FollowUpDialogue.objects.filter(session=s2).delete()
    for q_data in s2.concept_breakdown:
        if q_data.get("followup_prompt"):
            FollowUpDialogue.objects.create(
                session=s2,
                question_index=q_data["question_index"],
                candidate_initial_answer=q_data["transcript"],
                probe_type="system_scale",
                ai_followup_prompt=q_data["followup_prompt"],
                candidate_followup_answer=q_data.get("followup_response", "")
            )

    print(f"  [Created] Session 2: {s2.id} (Amazon Systems Architect • Composite {s2.overall_score})")

    # =========================================================================
    # Session 3: Meta Engineering Lead (Behavioral & STAR Leadership)
    # =========================================================================
    s3_id = uuid.UUID('33333333-4444-5555-6666-777777777773')
    InterviewSession.objects.filter(id=s3_id).delete()

    s3 = InterviewSession.objects.create(
        id=s3_id,
        role="Engineering Manager",
        company="Meta",
        track="Behavioral",
        seniority_level="Staff / Lead",
        interviewer_name="Sarah",
        interviewer_accent="US English (Standard)",
        coding_language="none",
        status="completed",
        overall_score=87.2,
        score_technical_depth=88.0,
        score_structural_logic=89.0,
        score_speech_clarity=86.0,
        score_body_language=85.0,
        feedback_summary={
            "criticalGaps": [
                "Quantify the specific engineer-hours saved following the automated testing framework rollout.",
                "Detail long-term career progression outcomes for junior engineers mentored during the re-architecture."
            ],
            "recommendations": [
                {"title": "Impact Metrics", "description": "Include explicit percentage reductions in production bug escape rates in executive summaries."},
                {"title": "Conflict De-escalation", "description": "Highlight empathetic listening techniques alongside data-driven benchmarking spikes."},
                {"title": "Vocal Modulation", "description": "Good conversational flow calibrated to your natural cadence. Vocal inflection remained poised and authoritative throughout."}
            ],
            "strengths": [
                "Exemplary STAR structuring with clear demarcation of Situation, Task, Action, and Measurable Result.",
                "Strong accountability instinct: framed failure as an opportunity for blameless system hardening.",
                "Exceptional eye contact (92% centered) and natural conversational pauses during high-stakes scenario walkthroughs."
            ]
        },
        concept_breakdown=[
            {
                "question_index": 0,
                "question_title": "Production Incident Post-Mortem & Blameless Accountability",
                "timestamp_start": 0.0,
                "timestamp_end": 115.0,
                "duration_formatted": "00:00 - 01:55",
                "score": 89,
                "transcript": "Situation: During a major infrastructure migration, an undetected race condition in our automated schema migration tool caused a 0.4% replication latency spike for messaging users. Task: As tech lead, I needed to halt the rollout, restore replica health, and safeguard user message delivery. Action: I immediately triggered our P0 response playbook, paused shard writes, rolled back the replica to the last stable snapshot, and led a blameless post-mortem that identified missing concurrency tests in our staging harness. Result: We engineered an automated shadow-traffic verification gate, successfully preventing similar regressions across the next four quarterly releases.",
                "code": "",
                "followup_prompt": "How did you manage stakeholder anxiety and rebuild trust with product leadership after the rollback?",
                "followup_response": "I published transparent status updates every 30 minutes with real-time replication graphs, followed by a collaborative post-mortem doc within 24 hours. Showing preventative engineering gates immediately restored confidence.",
                "covered_concepts": [
                    {"concept": "STAR Methodology", "evidence": "Structured Situation, Task, Action, and Measurable Result"},
                    {"concept": "Blameless Post-Mortem", "evidence": "Focus on root cause and preventative harness"},
                    {"concept": "Incident Leadership", "evidence": "Triggered P0 playbook and shard rollback"}
                ],
                "missing_concepts": [],
                "feedback": "Outstanding executive communication. Demonstrated deep ownership and psychological safety for the team."
            },
            {
                "question_index": 1,
                "question_title": "Technical Disagreement & Data-Driven Consensus",
                "timestamp_start": 115.0,
                "timestamp_end": 225.0,
                "duration_formatted": "01:55 - 03:45",
                "score": 85,
                "transcript": "Situation: A deadlock occurred between our backend microservices team and client engineers regarding whether to adopt GraphQL Federation or gRPC over HTTP/2 for mobile feed aggregation. Task: As lead, I needed to resolve the stalemate without fracturing team morale or slipping the quarterly release date. Action: I proposed a time-boxed 2-week benchmarking spike, measuring battery drain, payload compression, and p99 deserialization latencies across low-bandwidth cellular networks. Result: The benchmark showed gRPC reduced client deserialization CPU by 38%, which persuaded both teams to adopt gRPC for mobile APIs while keeping GraphQL for desktop consoles.",
                "code": "",
                "followup_prompt": "How did you ensure the engineers who initially strongly favored GraphQL felt valued and remained motivated?",
                "followup_response": "I invited them to lead the desktop API architecture where GraphQL truly excelled, ensuring their domain expertise directly shaped our production web stack.",
                "covered_concepts": [
                    {"concept": "Data-Driven Resolution", "evidence": "Time-boxed empirical benchmarking spike"},
                    {"concept": "Stakeholder Alignment", "evidence": "United cross-functional mobile and web teams"},
                    {"concept": "Empathy & Motivation", "evidence": "Channelled dissenting expertise productively"}
                ],
                "missing_concepts": [],
                "feedback": "Masterclass in constructive dissent and collaborative leadership."
            }
        ],
        telemetry_matrix={
            "integrity_telemetry": {
                "gaze_centered_percentage": 92,
                "posture_poise_percentage": 90,
                "average_pitch_variance_hz": 15.6,
                "reading_saccades_detected": 0,
                "lip_sync_mismatch_frames": 0,
                "integrity_status": "Verified (Organic)"
            },
            "calibrated_baseline": {
                "pitch_mean": 128.0,
                "pitch_std": 15.6,
                "cadence_sps": 3.6
            }
        }
    )

    QuestionRecord.objects.filter(session=s3).delete()
    for q_data in s3.concept_breakdown:
        QuestionRecord.objects.create(
            session=s3,
            question_index=q_data["question_index"],
            title=q_data["question_title"],
            text=q_data["transcript"],
            starter_code=q_data.get("code", ""),
            candidate_code=q_data.get("code", ""),
            candidate_transcript=q_data["transcript"],
            score=q_data["score"],
            evaluation_details={"covered": q_data["covered_concepts"], "feedback": q_data["feedback"]}
        )

    FollowUpDialogue.objects.filter(session=s3).delete()
    for q_data in s3.concept_breakdown:
        if q_data.get("followup_prompt"):
            FollowUpDialogue.objects.create(
                session=s3,
                question_index=q_data["question_index"],
                candidate_initial_answer=q_data["transcript"],
                probe_type="leadership_consensus",
                ai_followup_prompt=q_data["followup_prompt"],
                candidate_followup_answer=q_data.get("followup_response", "")
            )

    print(f"  [Created] Session 3: {s3.id} (Meta Engineering Manager • Composite {s3.overall_score})")
    print("Database seeding completed successfully.")


if __name__ == '__main__':
    seed_mock_results()
