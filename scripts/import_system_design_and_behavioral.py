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

from api.models import CatalogQuestion, InterviewQuestion


def import_system_design_primer():
    sd_base = Path(__file__).resolve().parent.parent / "data" / "system_design_primer" / "solutions" / "system_design"
    if not sd_base.exists():
        print(f"System design directory not found at {sd_base}")
        return

    print("Importing System Design questions from system-design-primer...")
    count = 0
    for folder in sd_base.iterdir():
        if not folder.is_dir():
            continue
        readme = folder / "README.md"
        if not readme.exists():
            continue

        raw_text = readme.read_text(encoding="utf-8", errors="ignore")
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        title_line = lines[0] if lines else folder.name.replace("_", " ").title()
        title = re.sub(r'^[#\s*]+', '', title_line).strip()
        slug = f"sd_{folder.name}"

        # Extract prompt overview (first 3-4 paragraphs)
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip() and not p.startswith("*Note") and not p.startswith("<img")]
        prompt_text = "\n\n".join(paragraphs[1:4]) if len(paragraphs) > 2 else f"Design a scalable, highly available distributed architecture for {title}."

        keywords = [
            "load_balancer", "horizontal_scaling", "caching", "database_replication",
            "sharding", "cdn", "microservices", "cap_theorem", "latency", "throughput",
            "data_modeling", "api_gateway", "asynchronous_processing", "message_queue"
        ]

        # 1. CatalogQuestion
        cq, created = CatalogQuestion.objects.update_or_create(
            question_key=slug,
            defaults={
                "title": title,
                "category": "System Design",
                "difficulty": "Hard",
                "prompt": f"{title}\n\n{prompt_text}",
                "starter_code": "",
                "sample_solution": raw_text[:3000],  # Full architecture overview
                "required_keywords": keywords[:8],
                "bonus_keywords": ["partitioning", "consistency_models", "rate_limiting", "circuit_breaker"],
                "rubric_breakdown": {
                    "architecture": 30,
                    "data_modeling": 25,
                    "scalability": 25,
                    "tradeoffs": 20
                },
                "child_concept_groups": [
                    {"parent": "caching", "children": ["redis", "cdn", "cache_invalidation"]},
                    {"parent": "database_replication", "children": ["read_replicas", "sharding", "failover"]}
                ]
            }
        )

        # 2. InterviewQuestion
        InterviewQuestion.objects.update_or_create(
            source_id=f"iq_{slug}",
            defaults={
                "technology": "system_design",
                "technology_name": "System Design & Distributed Systems",
                "difficulty": 3,
                "difficulty_label": "Hard",
                "question_type": "SYSTEM_DESIGN",
                "prompt": f"{title}\n\n{prompt_text}",
                "answer": raw_text[:1500],
                "explanation": f"Key architectural components for {title}: Load Balancing, Caching, Sharded Storage, Asynchronous Queue Workers.",
                "tags": ["system_design", "distributed_systems", folder.name, "scalability"],
                "source_metadata": {"source": "system-design-primer", "folder": folder.name},
                "is_active": True
            }
        )
        count += 1

    print(f"Imported {count} System Design problems from system-design-primer.")


BEHAVIORAL_QUESTION_BANK = [
    {
        "key": "beh_conflict_resolution",
        "title": "Technical Disagreement & Conflict Resolution",
        "prompt": "Tell me about a time when you strongly disagreed with a technical design, architecture decision, or product priority pushed by a peer, tech lead, or product manager. How did you handle the discussion, what data or prototypes did you use to substantiate your perspective, and what was the ultimate resolution?",
        "topics": ["conflict_resolution", "collaboration", "persuasion", "data_driven_decision"],
        "difficulty": "Medium",
        "expected_points": ["Context of disagreement", "Constructive discussion without hostility", "Data or proof of concept used", "Commitment to team decision (Disagree & Commit)"]
    },
    {
        "key": "beh_failure_postmortem",
        "title": "Production Incident, Failure & Accountability",
        "prompt": "Describe a significant technical failure, bug, or production outage that occurred on a system you built or maintained. Walk me through how you discovered it, how you communicated with users and leadership under pressure, the immediate remediation steps taken, and what structural changes were implemented in the post-mortem to guarantee it cannot recur.",
        "topics": ["accountability", "crisis_management", "post_mortem", "root_cause_analysis"],
        "difficulty": "Medium",
        "expected_points": ["Honest admission and discovery", "Containment and crisis triage", "Blameless root cause investigation", "Long-term preventative safeguards"]
    },
    {
        "key": "beh_ambiguity_requirements",
        "title": "Delivering Under Ambiguity & Shifting Requirements",
        "prompt": "Give an example of a project where the requirements were initially ambiguous, poorly specified, or changing rapidly week over week. How did you break the problem down into manageable milestones, validate assumptions with stakeholders, and deliver incremental value on schedule?",
        "topics": ["ambiguity", "scoping", "incremental_delivery", "leadership"],
        "difficulty": "Medium",
        "expected_points": ["Clarified unknown requirements", "Defined MVP milestones", "Maintained rapid feedback loop", "Delivered tangible business value"]
    },
    {
        "key": "beh_mentorship_culture",
        "title": "Mentorship & Raising the Engineering Bar",
        "prompt": "Describe how you have mentored a more junior engineer or helped elevate the engineering standards across your team (such as introducing automated testing, improving code review rigor, or revamping CI/CD pipelines). What challenges did you encounter when driving adoption, and how did you measure success?",
        "topics": ["mentorship", "engineering_culture", "influence_without_authority", "best_practices"],
        "difficulty": "Easy",
        "expected_points": ["Identified skill or quality gap", "Coached with patience and actionable feedback", "Drove team-wide adoption", "Measured improved velocity or lower defect rate"]
    },
    {
        "key": "beh_competing_priorities",
        "title": "Prioritization & Delivering Under High Pressure",
        "prompt": "Tell me about a situation where you were confronted with multiple urgent, competing deadlines from different stakeholders simultaneously. How did you prioritize what to build first, how did you push back or renegotiate timelines with empathy and data, and what was the outcome?",
        "topics": ["prioritization", "stakeholder_management", "time_management", "pushing_back"],
        "difficulty": "Medium",
        "expected_points": ["Impact vs Effort triage", "Transparent communication with stakeholders", "Reset expectations without panic", "Delivered high-ROI tasks successfully"]
    },
    {
        "key": "beh_cross_functional_alignment",
        "title": "Cross-Functional Collaboration with Non-Engineers",
        "prompt": "Can you describe a project where you had to work closely with non-technical partners (such as marketing, legal, sales, or design) who had very different expectations or limited technical background? How did you bridge the communication gap and align everyone on a shared vision?",
        "topics": ["cross_functional", "communication", "empathy", "stakeholder_alignment"],
        "difficulty": "Easy",
        "expected_points": ["Translated technical trade-offs into plain business terms", "Listened actively to partner needs", "Established clear shared milestones", "Delivered cross-functional alignment"]
    },
    {
        "key": "beh_proactive_initiative",
        "title": "Taking Ownership Beyond Your Core Scope",
        "prompt": "Walk me through a time when you identified a major problem, bottleneck, or opportunity that was strictly outside your assigned responsibilities, but you took the initiative to fix or build it anyway. What motivated you, what obstacles did you overcome, and what was the impact on the organization?",
        "topics": ["ownership", "bias_for_action", "innovation", "impact"],
        "difficulty": "Hard",
        "expected_points": ["Proactively spotted systemic inefficiency", "Took initiative without waiting for orders", "Overcame resource or prioritization hurdles", "Generated measurable positive impact"]
    },
    {
        "key": "beh_customer_obsession",
        "title": "Customer Empathy & Delivering User Impact",
        "prompt": "Give an example of when you advocated for the customer or end-user experience when technical or business pressures were nudging the team toward an inferior shortcut. How did you balance user empathy with technical feasibility and delivery constraints?",
        "topics": ["customer_empathy", "product_intuition", "advocacy", "user_impact"],
        "difficulty": "Medium",
        "expected_points": ["Identified user pain point", "Resisted short-sighted shortcuts", "Engineered feasible compromise", "Achieved superior user outcome"]
    }
]


def import_behavioral_questions():
    print("Importing curated Behavioral & Leadership questions...")
    count = 0
    for q in BEHAVIORAL_QUESTION_BANK:
        slug = q["key"]
        CatalogQuestion.objects.update_or_create(
            question_key=slug,
            defaults={
                "title": q["title"],
                "category": "Behavioral",
                "difficulty": q["difficulty"],
                "prompt": q["prompt"],
                "starter_code": "",  # Strictly no code!
                "sample_solution": "Exemplary STAR Response: Situation, Task, Action, and Quantified Result.",
                "required_keywords": ["situation", "task", "action", "result", "metric", "stakeholder", "lessons_learned"],
                "bonus_keywords": ["disagree_and_commit", "root_cause", "impact", "post_mortem", "ownership"],
                "rubric_breakdown": {
                    "situation_task": 20,
                    "action_ownership": 35,
                    "quantified_result": 25,
                    "self_reflection": 20
                },
                "child_concept_groups": [
                    {"parent": "action", "children": ["metric", "stakeholder"]},
                    {"parent": "result", "children": ["lessons_learned", "impact"]}
                ]
            }
        )

        InterviewQuestion.objects.update_or_create(
            source_id=f"iq_{slug}",
            defaults={
                "technology": "behavioral",
                "technology_name": "Behavioral & Leadership Principles",
                "difficulty": 2 if q["difficulty"] == "Medium" else (1 if q["difficulty"] == "Easy" else 3),
                "difficulty_label": q["difficulty"],
                "question_type": "BEHAVIORAL",
                "prompt": q["prompt"],
                "answer": "\n".join(f"- {p}" for p in q["expected_points"]),
                "explanation": f"Evaluation Rubric: Candidate must use the STAR method. Key competencies evaluated: {', '.join(q['topics'])}.",
                "tags": ["behavioral", "hr", "leadership", "star_method"] + q["topics"],
                "source_metadata": {"topics": q["topics"], "expected_points": q["expected_points"]},
                "is_active": True
            }
        )
        count += 1

    print(f"Imported {count} curated Behavioral questions into PostgreSQL.")


def import_core_engineering_concepts():
    print("Importing Core Engineering questions (OS, Databases, Networks, Concurrency)...")
    concepts = [
        {
            "key": "core_db_acid",
            "title": "ACID Properties & Database Isolation Levels",
            "prompt": "Explain the four ACID properties in relational databases. What is the difference between Read Committed, Repeatable Read, and Serializable isolation levels, and what specific anomalies (such as dirty reads, non-repeatable reads, or phantom reads) can occur under each?",
            "category": "Core Engineering",
            "keywords": ["atomicity", "consistency", "isolation", "durability", "dirty_read", "phantom_read", "serializable", "transactions"]
        },
        {
            "key": "core_os_process_thread",
            "title": "Processes, Threads, and Concurrency Invariants",
            "prompt": "What is the structural difference between a Process and a Thread in modern operating systems? How do memory address spaces, context switching costs, and inter-process communication (IPC) mechanisms differ?",
            "category": "Core Engineering",
            "keywords": ["virtual_memory", "address_space", "context_switch", "ipc", "shared_memory", "threads", "race_condition", "mutex"]
        },
        {
            "key": "core_net_tcp_udp",
            "title": "TCP vs UDP & The Three-Way Handshake",
            "prompt": "Compare TCP and UDP at the transport layer. Walk through the TCP three-way handshake and connection termination. How does TCP guarantee reliable, ordered delivery and congestion control compared to UDP?",
            "category": "Core Engineering",
            "keywords": ["three_way_handshake", "syn_ack", "congestion_control", "packet_loss", "sliding_window", "udp", "tcp", "latency"]
        },
        {
            "key": "core_sec_https_tls",
            "title": "HTTPS & The TLS 1.3 Handshake",
            "prompt": "How does HTTPS establish secure communication over an untrusted network? Walk through the cryptographic steps of the TLS handshake, including asymmetric key exchange, symmetric session keys, digital certificates, and Certificate Authorities.",
            "category": "Core Engineering",
            "keywords": ["tls", "asymmetric_encryption", "symmetric_encryption", "certificate_authority", "diffie_hellman", "private_key", "public_key"]
        }
    ]

    count = 0
    for c in concepts:
        slug = c["key"]
        CatalogQuestion.objects.update_or_create(
            question_key=slug,
            defaults={
                "title": c["title"],
                "category": "Core Engineering",
                "difficulty": "Medium",
                "prompt": c["prompt"],
                "starter_code": "",
                "sample_solution": f"Core engineering explanation of {c['title']}.",
                "required_keywords": c["keywords"][:6],
                "bonus_keywords": c["keywords"][6:],
                "rubric_breakdown": {"definition": 25, "mechanism": 35, "complexity": 25, "edge_cases": 15},
                "child_concept_groups": []
            }
        )

        InterviewQuestion.objects.update_or_create(
            source_id=f"iq_{slug}",
            defaults={
                "technology": "engineering_fundamentals",
                "technology_name": "Computer Science Fundamentals",
                "difficulty": 2,
                "difficulty_label": "Medium",
                "question_type": "TECHNICAL_CONCEPT",
                "prompt": c["prompt"],
                "answer": f"In-depth explanation covering: {', '.join(c['keywords'])}",
                "explanation": f"Fundamentals evaluation for {c['title']}.",
                "tags": ["cs_fundamentals", "operating_systems", "databases", "networking"],
                "source_metadata": {"category": c["category"]},
                "is_active": True
            }
        )
        count += 1

    print(f"Imported {count} Core Engineering questions into PostgreSQL.")


if __name__ == "__main__":
    print("Beginning System Design, Behavioral & Core Engineering Ingestion...")
    import_system_design_primer()
    import_behavioral_questions()
    import_core_engineering_concepts()
    print("PostgreSQL Ingestion Complete!")
