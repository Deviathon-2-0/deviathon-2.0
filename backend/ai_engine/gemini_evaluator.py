import json
import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Check the .env file in your project root."
    )

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(timeout=15000),
)

SYSTEM_INSTRUCTIONS = """
You are an evidence-based technical mock interview evaluator.

Evaluate the candidate's answer against the interview question and the supplied expected concepts.

CORE RULES:
1. Evaluate technical correctness, relevance, completeness, structure, and communication separately.
2. Never penalize Indian accents, regional pronunciation, dialect, or grammatical variation.
3. Award credit for technically correct explanations even when the candidate uses different wording.
4. Judge understanding from the meaning of the explanation, not keyword matching alone.
5. Identify each expected concept as covered, partial, missing, or incorrect.
6. Base content scoring primarily on the supplied expected concepts.
7. Do not invent additional mandatory requirements or deduct marks for omitting optional details that are not in the expected concepts.
8. Additional technical details may be mentioned in feedback, but must not reduce the content score unless they reveal a factual error or are explicitly required by the question or expected concepts.
9. If a candidate correctly explains an expected concept at the level requested, mark it covered. Do not downgrade it merely because the explanation could contain more detail.
10. If a candidate makes a factual claim that contradicts established technical knowledge, identify the error and explain its effect on the answer.
11. Distinguish an irrelevant answer from a poorly structured answer. An irrelevant answer can still be logically organized.
12. Never invent timestamps. Use null when reliable timestamps are unavailable.
13. Return integer scores from 0 to 100.
14. Return valid JSON only.

SCORING:
- content: Technical correctness, relevance, and coverage of the supplied expected concepts.
- structure: Logical organization, sequencing, and flow, independent of technical correctness.
- communication: Clarity and understandability of the transcript. Do not use accent or dialect as a proxy for communication quality.

CONTENT SCORING GUIDANCE:
- Start from the supplied expected concepts and assess each one individually.
- Covered: The candidate explains the expected concept correctly at an appropriate level.
- Partial: The candidate demonstrates some understanding but leaves a meaningful gap or gives an incomplete explanation.
- Missing: The candidate does not address the concept.
- Incorrect: The candidate explicitly gives a materially incorrect explanation of the concept.
- Do not count optional details as missing expected concepts.
- Do not reward irrelevant technical terminology merely because it appears in the answer.
- A concise, correct answer can receive a high content score.
- A longer answer must not automatically receive a higher score.
- Keep scores consistent with the concept assessments and explain substantial deductions.

FEEDBACK:
For every feedback item, provide a specific observation and an actionable suggestion.
Use short transcript quotations as evidence when possible.
Prioritize the most important improvement instead of listing optional details as mandatory corrections.
Flag uncertainty rather than pretending to know.
EVIDENCE RULES:
- Evidence must be an exact, verbatim quotation from the candidate's transcript.
- Never paraphrase, correct, or reconstruct a quotation.
- Every non-null evidence value must match a substring of the transcript exactly.
- If no exact quotation supports a concept, use null for evidence.
- Assess the meaning of the quoted words semantically; do not require the candidate to use the expected concept's exact wording.

OUTPUT:
Follow the requested JSON structure exactly.
Return scores as integers from 0 to 100.
Use null when reliable timestamps are unavailable.
Do not include markdown or explanatory text outside the JSON.
"""

def evaluate_with_gemini(question, expected_points, transcript):
    """
    Evaluate an interview answer using Gemini.
    Uses concept IDs instead of matching paraphrased concept strings.
    """

    if not transcript or not transcript.strip():
        raise ValueError("The transcript cannot be empty.")

    if not expected_points:
        raise ValueError("Expected evaluation points cannot be empty.")

    concepts = [
        {"concept_id": index, "description": point}
        for index, point in enumerate(expected_points)
    ]

    request_data = {
        "question": question,
        "expected_concepts": concepts,
        "candidate_transcript": transcript,
        "instructions": (
            "Evaluate every expected concept. Return its original concept_id. "
            "Judge meaning, not exact wording. Do not omit any concept."
        ),
        "required_output": {
            "scores": {
                "content": "integer 0-100",
                "structure": "integer 0-100",
                "communication": "integer 0-100"
            },
            "concept_analysis": [
                {
                    "concept_id": 0,
                    "status": "covered, partial, missing, or incorrect",
                    "evidence": "exact transcript quotation or null",
                    "explanation": "brief explanation"
                }
            ],
            "feedback": [
                {
                    "category": "content, structure, or communication",
                    "observation": "specific observation",
                    "suggestion": "actionable suggestion",
                    "timestamp_seconds": None
                }
            ],
            "summary": "short overall assessment"
        }
    }

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=json.dumps(request_data),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini returned invalid JSON.") from exc

    # Validate scores
    scores = result.get("scores", {})

    for name in ("content", "structure", "communication"):
        score = scores.get(name)

        if (
            not isinstance(score, int)
            or isinstance(score, bool)
            or not 0 <= score <= 100
        ):
            raise ValueError(f"Invalid or missing score: {name}")

    # Validate concept analysis using IDs
    concept_analysis = result.get("concept_analysis")

    if not isinstance(concept_analysis, list):
        raise ValueError("Missing or invalid concept_analysis.")

    expected_ids = set(range(len(expected_points)))
    assessed_ids = set()
    valid_statuses = {"covered", "partial", "missing", "incorrect"}

    for item in concept_analysis:
        if not isinstance(item, dict):
            raise ValueError("Invalid concept analysis entry.")

        concept_id = item.get("concept_id")
        status = item.get("status")
        evidence = item.get("evidence")

        if (
            not isinstance(concept_id, int)
            or isinstance(concept_id, bool)
            or concept_id not in expected_ids
        ):
            raise ValueError(f"Invalid concept ID: {concept_id}")

        if concept_id in assessed_ids:
            raise ValueError(f"Duplicate concept ID: {concept_id}")

        if status not in valid_statuses:
            raise ValueError(f"Invalid concept status: {status}")

        if evidence is not None:
            if not isinstance(evidence, str):
                raise ValueError("Evidence must be a string or null.")

            if evidence.strip():
                normalized_evidence = " ".join(evidence.split())
                normalized_transcript = " ".join(transcript.split())

                if normalized_evidence not in normalized_transcript:
                    raise ValueError(
                        f"Evidence is not present in transcript: {concept_id}"
                    )

        if status == "covered" and not (
            isinstance(evidence, str) and evidence.strip()
        ):
            raise ValueError(
                f"Covered concept requires evidence: {concept_id}"
            )

        assessed_ids.add(concept_id)

        # Restore the original concept for the rest of the application.
        item["concept"] = expected_points[concept_id]
        item.pop("concept_id", None)

    missing_ids = expected_ids - assessed_ids

    if missing_ids:
        raise ValueError(f"Missing concept assessments: {sorted(missing_ids)}")

    # Validate feedback
    feedback = result.get("feedback")

    if not isinstance(feedback, list):
        raise ValueError("Missing or invalid feedback.")

    valid_categories = {"content", "structure", "communication"}

    for item in feedback:
        if not isinstance(item, dict):
            raise ValueError("Invalid feedback entry.")

        if item.get("category") not in valid_categories:
            raise ValueError("Invalid feedback category.")

        if not isinstance(item.get("observation"), str) or not item["observation"].strip():
            raise ValueError("Feedback observation cannot be empty.")

        if not isinstance(item.get("suggestion"), str) or not item["suggestion"].strip():
            raise ValueError("Feedback suggestion cannot be empty.")

    result["transcript"] = transcript

    return result