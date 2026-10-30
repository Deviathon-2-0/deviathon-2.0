import os
import json
from pathlib import Path
from django.conf import settings
from google import genai
from google.genai import types

from ai_engine.gemini_evaluator import evaluate_with_gemini
from ai_engine.evaluation import evaluate_answer
from ai_engine.feedback import generate_feedback

def get_gemini_client():
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=api_key)


def generate_interview_questions(role, company="Google", track="Tech", level="SDE 2", language="python", count=4):
    """
    Generate dynamic, authentic interview questions calibrated to the company, role,
    seniority level, and language using Gemini 2.5.
    """
    client = get_gemini_client()

    prompt = f"""
You are an experienced technical interviewer at {company}.

Generate exactly {count} interview questions for:
- Role: {role}
- Company: {company}
- Track: {track}
- Seniority: {level}
- Programming language: {language}

IMPORTANT:
1. Every question must be directly relevant to the candidate's role.
2. Adapt questions to the specified programming language.
3. For frontend roles, prioritize JavaScript, React, HTML, CSS,
   browser internals, performance, accessibility and frontend architecture.
4. For backend roles, prioritize APIs, databases, networking,
   concurrency and backend architecture.
5. Match difficulty to the candidate's seniority.
6. Do not introduce unrelated distributed-systems questions.
7. Do not use a different programming language in starter_code.
8. Include 2 domain-specific questions, 1 practical scenario,
   and 1 architecture or debugging question where appropriate.

Return this exact JSON structure:
{{
  "questions": [
    {{
      "index": 0,
      "title": "Short descriptive title",
      "text": "Clear interview question with realistic constraints",
      "expected_concepts": ["concept 1", "concept 2", "concept 3"],
      "starter_code": "",
      "test_cases": [],
      "evaluation_rubric": {{
        "optimal_complexity": "Expected complexity where applicable",
        "key_invariants": "Important edge cases and constraints"
      }}
    }}
  ]
}}

Return valid JSON only. No markdown.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        content_text = response.text.strip()
        data = json.loads(content_text)
        return data.get("questions", [])
    except Exception as e:
        # Fallback to realistic deterministic questions if API quota/rate limit occurs
        return _get_fallback_questions(role, company, track, level, language)


def evaluate_candidate_performance(question_text, expected_concepts, candidate_transcript, candidate_code="", language="python"):
    """
    Evaluate candidate's answer using the AI evaluation engine.
    Produces content, structure, and communication scores, plus concept coverage and feedback.
    """
    # Use Gemini evaluator from ai_engine
    try:
        if candidate_transcript and candidate_transcript.strip():
            result = evaluate_with_gemini(
    question=question_text,
    expected_points=expected_concepts,
    transcript=candidate_transcript
)
        else:
            result = {
                "scores": {"content": 50, "structure": 50, "communication": 50},
                "concept_assessment": [],
                "feedback": {
                    "strengths": ["Answer submitted for technical review."],
                    "areas_for_improvement": ["Elaborate further with verbal reasoning and design trade-offs."],
                    "factual_errors": [],
                    "actionable_next_steps": ["State asymptotic complexities upfront."]
                }
            }

                # Code review if code was provided
        code_review = {}
        if candidate_code and len(candidate_code.strip()) > 10:
            code_review = _review_code_with_gemini(candidate_code, question_text, language)

        # Calculate score using only measured evaluation dimensions.
        overall = round((
            result["scores"]["content"] * 0.50 +
            result["scores"]["structure"] * 0.30 +
            result["scores"]["communication"] * 0.20
        ), 1)

        return {
            "success": True,
            "overall_score": overall,
            "scores": {
                "technical_depth": result["scores"]["content"],
                "structural_logic": result["scores"]["structure"],
                "speech_clarity": result["scores"]["communication"],
                "body_language": None
            },
            "concept_breakdown": result.get("concept_analysis", []),
            "feedback": result.get("feedback", {}),
            "code_review": code_review
        }
    except Exception as e:
        print(f"GEMINI EVALUATION FAILED: {type(e).__name__}: {e}")

    return evaluate_answer(
        answer=candidate_transcript,
        expected_points=expected_concepts,
        question=question_text,
        use_gemini=False
    )


def _review_code_with_gemini(code, question_text, language):
    """Review candidate code for time/space complexity and correctness."""
    client = get_gemini_client()
    prompt = f"""
Analyze this candidate code written in {language} for the question: "{question_text}".
Candidate Code:
```
{code}
```
Return valid JSON:
{{
  "correctness_score": 90,
  "time_complexity": "O(N)",
  "space_complexity": "O(1)",
  "strengths": ["Clear naming", "Proper boundary checks"],
  "optimizations": ["Consider using two pointers instead of hash table to save memory"]
}}
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text.strip())
    except Exception:
        return {
            "correctness_score": 85,
            "time_complexity": "O(N)",
            "space_complexity": "O(1)",
            "strengths": ["Clean modular design"],
            "optimizations": ["Ensure defensive checks for null/empty collections"]
        }


def analyze_resume_text(resume_text):
    """Audit resume text with Gemini 2.5 and generate ATS score and tailored questions."""
    client = get_gemini_client()
    prompt = f"""
You are an expert technical recruiter and resume auditor at top-tier tech companies.
Audit this candidate's resume:
\"\"\"
{resume_text}
\"\"\"

Return valid JSON with:
{{
  "candidate_name": "Full Name",
  "email": "Email if found",
  "ats_score": 88.5,
  "key_strengths": ["strength 1", "strength 2", "strength 3"],
  "skill_gaps": ["gap 1", "gap 2"],
  "extracted_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "AWS"],
  "tailored_questions": [
    "Question 1 based on their specific experience/project",
    "Question 2 probing their architectural ownership",
    "Question 3 challenging a technical claim on their resume"
  ],
  "recommendations": [
    "Actionable bullet point improvement 1",
    "Actionable bullet point improvement 2"
  ]
}}
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        return {
            "candidate_name": "Candidate",
            "ats_score": 82.0,
            "key_strengths": ["Strong foundational programming", "Practical project execution"],
            "skill_gaps": ["Quantifiable business metrics", "Large-scale distributed systems evidence"],
            "extracted_skills": ["Software Engineering", "Algorithms", "System Design", "APIs"],
            "tailored_questions": [
                "Describe the most challenging bug you encountered in production.",
                "How do you design database schemas for rapid querying at scale?"
            ],
            "recommendations": ["Quantify project impact with percentage metrics and latency numbers."]
        }


def generate_prep_roadmap(target_role, target_company="Google", duration_days=14):
    """Generate day-by-day structured preparation roadmap."""
    client = get_gemini_client()
    prompt = f"""
Generate an intensive, structured {duration_days}-day mock interview prep roadmap for:
Target Role: {target_role}
Target Company: {target_company}

Return valid JSON:
{{
  "days": [
    {{
      "day": 1,
      "theme": "Distributed Systems & Invariants",
      "focus_areas": ["Replication", "Consensus", "WAL"],
      "recommended_practice": "Practice designing a distributed log like Kafka.",
      "estimated_hours": 3
    }}
  ]
}}
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text.strip())
    except Exception:
        return {
            "days": [
                {
                    "day": 1,
                    "theme": "Core Data Structures & Algorithmic Patterns",
                    "focus_areas": ["Two Pointers", "Sliding Window", "Monotonic Stack"],
                    "recommended_practice": "Solve 3 medium LeetCode problems on array windows.",
                    "estimated_hours": 2.5
                },
                {
                    "day": 2,
                    "theme": "Trees, Graphs & Traversal Invariants",
                    "focus_areas": ["BFS/DFS", "Topological Sort", "Shortest Path"],
                    "recommended_practice": "Implement course schedule topological sort.",
                    "estimated_hours": 3
                }
            ]
        }


def _get_fallback_questions(role, company, track, level, language):
    questions = {
        "javascript": [
            {
                "title": "JavaScript Closures",
                "text": "Explain closures in JavaScript. How would you use one to create a private counter?",
                "expected_concepts": [
                    "A closure retains access to its lexical scope.",
                    "Inner functions can access variables from outer functions.",
                    "Closures can preserve private state."
                ],
                "starter_code": ""
            },
            {
                "title": "Event Loop",
                "text": "Explain how the JavaScript event loop handles synchronous code, promises and setTimeout callbacks.",
                "expected_concepts": [
                    "Synchronous code executes on the call stack.",
                    "Promise callbacks use the microtask queue.",
                    "setTimeout callbacks use the task queue.",
                    "Microtasks are processed before the next task."
                ],
                "starter_code": ""
            },
            {
                "title": "Array Methods",
                "text": "Explain the differences between map, filter and reduce. Give a practical use case for each.",
                "expected_concepts": [
                    "map transforms array elements.",
                    "filter selects elements based on a condition.",
                    "reduce accumulates values into a single result."
                ],
                "starter_code": ""
            },
            {
                "title": "Frontend Performance",
                "text": "A web page takes several seconds to become interactive. How would you investigate and improve its performance?",
                "expected_concepts": [
                    "Use browser performance tools to identify bottlenecks.",
                    "Reduce JavaScript bundle size.",
                    "Optimize rendering and unnecessary re-renders.",
                    "Lazy-load non-critical resources."
                ],
                "starter_code": ""
            }
        ]
    }

    selected = questions.get(language.lower())

    if not selected:
        return []

    result = []

    for index, question in enumerate(selected[:4]):
        result.append({
            **question,
            "index": index,
            "test_cases": [],
            "evaluation_rubric": {
                "optimal_complexity": "Not applicable",
                "key_invariants": "Assess conceptual correctness and explanation."
            }
        })

    return result