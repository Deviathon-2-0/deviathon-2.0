"""
Self-Learning Accent Miner (backend/evaluator/async_learner.py)
Implements Tier 3: Asynchronous, zero-lag background worker using Gemini 2.5 Flash
to automatically detect, mine, and cache acoustic mishearings of computer science
and engineering terminology from regional accent transcripts.

Candidate HTTP responses are NEVER delayed by this miner; execution runs in a daemon thread.
"""
import os
import json
import logging
import threading
from typing import List, Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from evaluator.accent_normalizer import save_to_accent_registry, PHONETIC_TECH_REGISTRY
except ImportError:
    from backend.evaluator.accent_normalizer import save_to_accent_registry, PHONETIC_TECH_REGISTRY

logger = logging.getLogger("imaira.async_learner")

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-flash-latest"
]


def _get_genai_client():
    """Initialize Google GenAI client using settings or environment variables."""
    if not GENAI_AVAILABLE:
        return None
    try:
        from django.conf import settings
        api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY")
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            logger.warning(f"Failed to init GenAI client with key: {e}")
    try:
        return genai.Client()
    except Exception:
        return None


def mine_and_cache_accent_terms(question_topic: str, raw_transcript: str) -> List[Dict[str, str]]:
    """
    Analyzes raw candidate transcript via Gemini for acoustic mishearings of CS terms.
    Appends newly discovered mishearing-to-canonical pairs into PHONETIC_TECH_REGISTRY
    and persists them to dynamic_accent_cache.json and database.

    Runs in a background worker / daemon thread so candidate responses have 0ms delay.
    """
    if not raw_transcript or len(raw_transcript.strip().split()) < 4:
        return []

    # Clean trivial placeholders
    clean_sample = raw_transcript.strip().lower()
    if clean_sample.startswith("[no verbal") or clean_sample.startswith("[no answer"):
        return []

    client = _get_genai_client()
    if not client:
        logger.info("GenAI client not available for async accent mining; using local registry.")
        return []

    prompt = f"""You are an expert computational phonetician and speech scientist specializing in technical English accent drift, particularly Indian English and regional acoustic slips.

Problem:
Standard Speech-to-Text (STT) models often misrecognize technical computer science words as common everyday words due to accent nuances (e.g. /v/ and /w/ interchange, trailing vowel drops, syllable-timed cadence, word-boundary conflations).
Examples:
- "has aman" or "has man" -> "hashmap"
- "two pulse" -> "tuples"
- "a symptomatic" -> "asymptotic"
- "wector clock" -> "vector clock"
- "red black tray" -> "red-black tree"
- "link least" -> "linked list"
- "dijkstra" -> "dice tra"
- "daemon" -> "demon thread"

Context:
- Interview Question / Topic: {question_topic or 'Computer Science / Software Engineering'}
- Raw Candidate Transcript:
"{raw_transcript}"

Task:
Examine the candidate's transcript for acoustic slips where technical computer science, algorithms, system design, or engineering terms were misheard or transcribed as phonetically adjacent non-technical or corrupted words.

Return ONLY a valid JSON array of objects. Do not wrap in markdown quotes if possible, or use standard ```json.
Format:
[
  {{"misheard_phrase": "<the exact misheard phrase in transcript, lowercase>", "canonical_tech_term": "<canonical correct technical term>"}}
]

If there are no acoustic mishearings in this transcript, return an empty JSON array: [].
"""

    discovered_terms: List[Dict[str, str]] = []

    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=600,
                    response_mime_type="application/json"
                ) if GENAI_AVAILABLE else None
            )

            text_output = (response.text or "").strip()
            if not text_output:
                continue

            # Strip possible markdown code fences
            if text_output.startswith("```json"):
                text_output = text_output[7:]
            elif text_output.startswith("```"):
                text_output = text_output[3:]
            if text_output.endswith("```"):
                text_output = text_output[:-3]
            text_output = text_output.strip()

            parsed = json.loads(text_output)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and "misheard_phrase" in item and "canonical_tech_term" in item:
                        misheard = str(item["misheard_phrase"]).strip().lower()
                        canonical = str(item["canonical_tech_term"]).strip().lower()
                        if misheard and canonical and misheard != canonical:
                            save_to_accent_registry(misheard, canonical)
                            discovered_terms.append({
                                "misheard_phrase": misheard,
                                "canonical_tech_term": canonical
                            })

                # Also persist to DB if Django model exists
                try:
                    from api.models import PhoneticGlossary
                    for pair in discovered_terms:
                        PhoneticGlossary.objects.get_or_create(
                            misheard_phrase=pair["misheard_phrase"],
                            defaults={
                                "canonical_term": pair["canonical_tech_term"],
                                "domain": question_topic or "General CS",
                                "source": "gemini_async_miner"
                            }
                        )
                except Exception as db_err:
                    logger.debug(f"PhoneticGlossary DB save note: {db_err}")

                logger.info(f"Async accent miner successfully learned {len(discovered_terms)} new acoustic terms via {model_name}.")
                break
        except Exception as e:
            logger.debug(f"Model {model_name} mining attempt notice: {e}")
            continue

    return discovered_terms


def dispatch_async_accent_mining(question_topic: str, raw_transcript: str) -> threading.Thread:
    """
    Dispatches accent mining in a non-blocking daemon thread.
    Returns the thread object immediately without waiting.
    """
    worker = threading.Thread(
        target=mine_and_cache_accent_terms,
        args=(question_topic, raw_transcript),
        daemon=True,
        name="AsyncAccentMiner"
    )
    worker.start()
    return worker
