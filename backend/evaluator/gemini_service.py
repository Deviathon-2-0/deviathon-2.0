"""
Gemini Tier-2 Fallback & Executive Synthesizer (evaluator/gemini_service.py)
Uses the official google-genai SDK with modern high-rate-limit models:
gemini-3.5-flash (primary deep analysis) with gemini-3.5-flash-lite (high RPM/low latency)
and seamless in-memory deterministic fallback.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    GENAI_SDK_AVAILABLE = True
except ImportError:
    GENAI_SDK_AVAILABLE = False


class GeminiEvaluationService:
    def __init__(self, model_name: str = "gemini-3.5-flash"):
        # Prioritize modern high-rate-limit models (Gemini 3.5 Flash & Flash-Lite)
        self.model_candidates = [
            model_name,
            "gemini-3.5-flash-lite",
            "gemini-3-flash-preview",
            "gemini-flash-latest"
        ]
        self.client = None
        self._init_client()

    def _init_client(self):
        if not GENAI_SDK_AVAILABLE:
            return
        api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.warning(f"Notice initializing Google GenAI client: {e}")
                self.client = None
        else:
            try:
                self.client = genai.Client()
            except Exception:
                self.client = None

    def synthesize_or_fallback(
        self,
        session_data: Dict[str, Any],
        deterministic_results: Dict[str, Any],
        timeline_moments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizes executive evaluation and coaching scorecard using Gemini 3.5 Flash / Flash-Lite,
        or gracefully falls back to deterministic template rendering.
        """
        if self.client:
            for model in self.model_candidates:
                try:
                    gemini_output = self._call_gemini_synthesis(model, session_data, deterministic_results, timeline_moments)
                    if gemini_output:
                        return {
                            **deterministic_results,
                            "synthesis_tier": f"Tier-2 (Google GenAI {model})",
                            "executive_summary": gemini_output.get("executive_summary", ""),
                            "strengths": gemini_output.get("strengths", []),
                            "targeted_coaching_tips": gemini_output.get("targeted_coaching_tips", []),
                            "suggested_follow_up": gemini_output.get("suggested_follow_up", ""),
                            "timeline_moments": timeline_moments
                        }
                except Exception as err:
                    logger.info(f"Model {model} failed or rate-limited ({err}); evaluating next candidate...")

        # Tier-1 Deterministic Synthesis Fallback
        return self._deterministic_fallback_synthesis(session_data, deterministic_results, timeline_moments)

    def _call_gemini_synthesis(
        self,
        model_name: str,
        session_data: Dict[str, Any],
        deterministic: Dict[str, Any],
        timeline: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Invokes Gemini with strict JSON schema enforcement."""
        prompt_payload = {
            "question": deterministic.get("question_title"),
            "candidate_transcript": session_data.get("transcript", ""),
            "normalized_transcript": session_data.get("normalized_transcript", ""),
            "deterministic_scores": {
                "overall_score": deterministic.get("overall_score"),
                "found_keywords": deterministic.get("keyword_coverage", {}).get("found_required", []),
                "missed_keywords": deterministic.get("keyword_coverage", {}).get("missed_required", []),
                "penalties": deterministic.get("delivery_penalties", [])
            },
            "timeline_moments": timeline[:6]
        }

        user_content = f"""Evaluate this candidate interview response based strictly on the factual data provided below:
{json.dumps(prompt_payload, indent=2)}

Provide your assessment in the following JSON schema:
{{
  "executive_summary": "Concise 2-sentence executive summary referencing exact technical competence and delivery tells.",
  "strengths": ["Specific strength 1 with exact technical concept", "Specific strength 2"],
  "targeted_coaching_tips": [
    {{
      "focus": "Algorithmic or Behavioral",
      "timestamp_reference": "e.g. 0:12s or Specific segment",
      "observation": "Exact tell or omission",
      "actionable_fix": "Concrete technical guidance (never say 'practice more')"
    }}
  ],
  "suggested_follow_up": "A targeted follow-up question addressing the candidate's biggest technical gap."
}}
"""

        response = self.client.models.generate_content(
            model=model_name,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an elite technical interviewer. Never give generic advice like 'practice more'. "
                    "Reference specific timestamps, filler words, and omitted algorithmic mechanics. "
                    "Return strictly valid JSON."
                ),
                response_mime_type="application/json",
                temperature=0.2,
            )
        )

        if response and response.text:
            return json.loads(response.text)
        return None

    def _deterministic_fallback_synthesis(
        self,
        session_data: Dict[str, Any],
        deterministic: Dict[str, Any],
        timeline: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """High-precision template-based executive synthesis without hallucinations."""
        score = deterministic.get("overall_score", 70.0)
        q_title = deterministic.get("question_title", "Technical Problem")
        found_kw = deterministic.get("keyword_coverage", {}).get("found_required", [])
        missed_kw = deterministic.get("keyword_coverage", {}).get("missed_required", [])
        penalties = deterministic.get("delivery_penalties", [])

        # Construct Executive Summary
        if score >= 85:
            summary = (
                f"Candidate exhibited strong technical command on '{q_title}', correctly articulating "
                f"{', '.join(found_kw[:3]) if found_kw else 'core algorithmic mechanics'} with high architectural precision."
            )
        elif score >= 65:
            summary = (
                f"Candidate provided a viable foundation on '{q_title}', but omitted critical algorithmic details "
                f"including {', '.join(missed_kw[:2]) if missed_kw else 'key edge-case mechanics'}."
            )
        else:
            summary = (
                f"Candidate struggled to articulate canonical concepts for '{q_title}', notably missing "
                f"{', '.join(missed_kw[:3]) if missed_kw else 'fundamental primitives'}."
            )

        # Construct Strengths
        strengths = []
        if found_kw:
            strengths.append(f"Accurately incorporated canonical keywords: {', '.join(found_kw)}.")
        if deterministic.get("technical_depth", {}).get("synergies_detected"):
            syn = deterministic["technical_depth"]["synergies_detected"][0]
            strengths.append(f"Strong concept linking between '{syn['parent']}' and {', '.join(syn['co_occurring_children'])}.")
        if not penalties:
            strengths.append("Maintained consistent gaze focus and vocal confidence throughout response.")
        elif len(strengths) == 0:
            strengths.append("Communicated clearly and attempted algorithmic breakdown.")

        # Construct Actionable Coaching Tips
        coaching_tips = []
        if missed_kw:
            coaching_tips.append({
                "focus": "Algorithmic Rigor",
                "timestamp_reference": "Full Response",
                "observation": f"Omitted explicit discussion of {', '.join(missed_kw)}.",
                "actionable_fix": f"When addressing {q_title}, immediately state how {missed_kw[0]} dictates runtime constraints."
            })

        for p in penalties:
            coaching_tips.append({
                "focus": "Behavioral Delivery",
                "timestamp_reference": "Telemetry Stream",
                "observation": p.get("reason", "Behavioral tell observed"),
                "actionable_fix": (
                    "Lock eye contact onto the webcam when explaining complex state transitions."
                    if p.get("type") == "GAZE_DROP" else
                    "Vary sentence inflection to highlight Big-O complexity figures."
                )
            })

        if not coaching_tips:
            coaching_tips.append({
                "focus": "Senior Architectural Polish",
                "timestamp_reference": "Conclusion",
                "observation": "Response ended without evaluating hardware/cache-locality trade-offs.",
                "actionable_fix": "Proactively mention CPU cache locality and memory fragmentation considerations."
            })

        # Suggested Follow-Up
        if missed_kw:
            follow_up = f"Could you walk me through how you would handle {missed_kw[0]} in a high-concurrency production environment?"
        else:
            follow_up = "How would you optimize this design if input data exceeds RAM and requires external disk paging?"

        return {
            **deterministic,
            "synthesis_tier": "Tier-1 (Deterministic Engine Fallback)",
            "executive_summary": summary,
            "strengths": strengths,
            "targeted_coaching_tips": coaching_tips,
            "suggested_follow_up": follow_up,
            "timeline_moments": timeline
        }
