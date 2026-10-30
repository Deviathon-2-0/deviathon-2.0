"""
Deterministic Rubric & Calibrated Behavioral Scorer (evaluator/deterministic_scorer.py)
Implements:
- Layer 1: Acoustic & Prosodic Analysis (dynamic pitch baseline calibration, syllable-timed cadence, cognitive pause tolerance)
- Layer 3: Decoupled Scoring (Delivery never deducts from Technical Depth; Technical Depth is strictly semantic & algorithmic)
"""
import re
import math
from typing import Dict, List, Any, Optional, Tuple
from evaluator.catalog import INTERVIEW_QUESTION_REGISTRY


def estimate_syllables(text: str) -> int:
    """Estimates syllable count using vowel group heuristics suitable for accent cadence."""
    cleaned = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    words = cleaned.split()
    total = 0
    for w in words:
        if len(w) <= 3:
            total += 1
            continue
        # Count vowel groups
        vowel_runs = len(re.findall(r'[aeiouy]+', w))
        if w.endswith('e') and not w.endswith('le') and vowel_runs > 1:
            vowel_runs -= 1
        total += max(1, vowel_runs)
    return max(total, 1)


class DeterministicScorer:
    def __init__(self, question_registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self.registry = question_registry or INTERVIEW_QUESTION_REGISTRY

    def evaluate(
        self,
        question_id: str,
        normalized_transcript: str,
        telemetry: Optional[List[Dict[str, Any]]] = None,
        calibrated_baseline: Optional[Dict[str, Any]] = None,
        duration_sec: float = 30.0
    ) -> Dict[str, Any]:
        """
        Runs decoupled Tier-1 deterministic evaluation:
        - Technical Depth: Evaluates concept graph & architectural keywords (0-100).
        - Delivery & Composure: Evaluates gaze & posture stability (0-100).
        - Speech Clarity & Modulation: Evaluates prosody relative to calibrated baseline (0-100).
        """
        question = self.registry.get(question_id)
        if not question:
            # Fallback to general technical problem solving rubric
            question = self.registry.get("default_general", {
                "id": question_id,
                "title": "Technical Problem Solving",
                "difficulty": "Medium",
                "required_keywords": ["time_complexity", "space_complexity", "O(1)"],
                "bonus_keywords": ["tradeoffs", "edge_cases"],
                "rubric_breakdown": {"definition": 25, "mechanism": 35, "complexity": 25, "edge_cases": 15},
                "child_concept_groups": []
            })

        transcript_lower = (normalized_transcript or "").lower()
        telemetry_stream = telemetry or []

        # ===================================================================
        # 1. Technical Depth Score (Semantic & Concept Coverage - Layer 3)
        # ===================================================================
        required_kw = question.get("required_keywords", [])
        bonus_kw = question.get("bonus_keywords", [])

        found_required = []
        missed_required = []
        for kw in required_kw:
            kw_clean = kw.lower()
            kw_spaced = kw_clean.replace("_", " ")
            if (kw_clean in transcript_lower) or (kw_spaced in transcript_lower):
                found_required.append(kw)
            else:
                missed_required.append(kw)

        found_bonus = []
        for kw in bonus_kw:
            kw_clean = kw.lower()
            kw_spaced = kw_clean.replace("_", " ")
            if (kw_clean in transcript_lower) or (kw_spaced in transcript_lower):
                found_bonus.append(kw)

        req_coverage_ratio = len(found_required) / max(len(required_kw), 1)
        bonus_coverage_ratio = len(found_bonus) / max(len(bonus_kw), 1) if bonus_kw else 0.0

        # Base rubric points (60% weight on required, 15% on bonus)
        keyword_score = (req_coverage_ratio * 60.0) + (bonus_coverage_ratio * 15.0)

        # Technical Depth & Child Concept Co-occurrence
        child_groups = question.get("child_concept_groups", [])
        depth_hits = 0
        depth_details = []
        for group in child_groups:
            parent = group["parent"].lower()
            children = [c.lower() for c in group.get("children", [])]
            parent_found = (parent in transcript_lower) or (parent.replace("_", " ") in transcript_lower)
            if parent_found:
                found_children = [c for c in children if (c in transcript_lower) or (c.replace("_", " ") in transcript_lower)]
                if found_children:
                    depth_hits += 1
                    depth_details.append({
                        "parent": parent,
                        "co_occurring_children": found_children,
                        "synergy": "HIGH"
                    })

        if child_groups:
            depth_score = (depth_hits / len(child_groups)) * 25.0
        else:
            tech_tokens = ["time_complexity", "space_complexity", "O(1)", "O(n)", "memory", "optimal", "constraint", "scalability"]
            hits = sum(1 for t in tech_tokens if t in transcript_lower)
            depth_score = min(25.0, hits * 5.0)

        raw_technical_score = min(100.0, keyword_score + depth_score)
        # Round technical score cleanly - NEVER DEDUCT DELIVERY PENALTIES FROM TECH SCORE!
        technical_depth_score = round(raw_technical_score, 1)

        # ===================================================================
        # 2. Acoustic & Prosodic Analysis (Layer 1 Dynamic Calibration)
        # ===================================================================
        baseline = calibrated_baseline or {}
        user_baseline_f0 = float(baseline.get("pitch_mean") or baseline.get("f0_mean") or 120.0)
        user_baseline_std = float(baseline.get("pitch_std") or baseline.get("f0_std") or 14.0)
        user_baseline_sps = float(baseline.get("cadence_sps") or 3.2)

        # Extract pitch values from telemetry stream
        pitches = [
            float(frame.get("pitch_hz", frame.get("pitch", 0.0)))
            for frame in telemetry_stream
            if float(frame.get("pitch_hz", frame.get("pitch", 0.0))) > 55.0
        ]

        has_vocal_audio = len(pitches) >= 3 and len(normalized_transcript.strip().split()) >= 3
        if pitches:
            mean_pitch = sum(pitches) / len(pitches)
            variance = sum((p - mean_pitch) ** 2 for p in pitches) / len(pitches)
            current_pitch_std = math.sqrt(variance)
        else:
            mean_pitch = 0.0
            current_pitch_std = 0.0

        # Syllables per second calculation
        syllables = estimate_syllables(normalized_transcript)
        effective_duration = max(duration_sec, 5.0)
        current_sps = round(syllables / effective_duration, 2)

        # Detect cognitive pauses (1.0s to 2.5s) vs prolonged dead-air (>4.0s)
        cognitive_pauses = 0
        dead_air_pauses = 0
        current_silent_duration = 0.0
        prev_t = 0.0

        for idx, frame in enumerate(telemetry_stream):
            t = float(frame.get("timestamp", idx * 0.5))
            dt = t - prev_t if idx > 0 else 0.5
            prev_t = t
            is_speaking = frame.get("is_speaking", frame.get("mic_rms", 0.05) > 0.015)
            if not is_speaking:
                current_silent_duration += dt
            else:
                if 1.0 <= current_silent_duration <= 2.5:
                    cognitive_pauses += 1  # Natural thought formulation pause (Positive composure tell)
                elif current_silent_duration > 4.0:
                    dead_air_pauses += 1   # Excessive dead air
                current_silent_duration = 0.0

        # Dynamic Monotone Pitch Check:
        dynamic_pitch_cutoff = max(3.0, user_baseline_std * 0.40)
        is_monotone = (current_pitch_std < dynamic_pitch_cutoff) and len(pitches) >= 8 and has_vocal_audio

        if not has_vocal_audio:
            speech_clarity_score = 0.0
            is_monotone = False
            modulation_feedback = "No spoken vocal audio detected during this question response."
        else:
            base_speech_score = 85.0
            if is_monotone:
                base_speech_score -= 10.0
            if dead_air_pauses > 0:
                base_speech_score -= min(15.0, dead_air_pauses * 5.0)
            if cognitive_pauses >= 1:
                base_speech_score += min(6.0, cognitive_pauses * 2.0)
            speech_clarity_score = round(max(40.0, min(98.0, base_speech_score)), 1)
            modulation_feedback = (
                "Good conversational flow calibrated to your natural cadence."
                if not is_monotone
                else "Pitch variance remained relatively steady; add deliberate vocal emphasis when highlighting key architectural points."
            )

        # ===================================================================
        # 3. Visual Tracking & Body Language Composure
        # ===================================================================
        max_consecutive_gaze_loss = 0.0
        current_gaze_loss = 0.0
        gaze_hits = 0
        reading_saccade_flags = 0

        posture_scores = []
        prev_t = None
        for frame in telemetry_stream:
            t = float(frame.get("timestamp", 0.0))
            dt = (t - prev_t) if prev_t is not None else 0.2
            prev_t = t

            is_looking = frame.get("eye_contact", frame.get("gaze_score", 1.0) >= 0.5)
            if is_looking:
                gaze_hits += 1
                current_gaze_loss = 0.0
            else:
                current_gaze_loss += max(dt, 0.1)
                if current_gaze_loss > max_consecutive_gaze_loss:
                    max_consecutive_gaze_loss = current_gaze_loss

            if frame.get("reading_saccades_detected", False):
                reading_saccade_flags += 1

            posture = frame.get("neck_ratio", frame.get("posture_score", 1.0))
            posture_scores.append(float(posture))

        has_video_telemetry = bool(telemetry_stream and any("eye_contact" in f or "neck_ratio" in f or "gaze_score" in f for f in telemetry_stream))

        if has_video_telemetry:
            gaze_ratio = (gaze_hits / max(len(telemetry_stream), 1))
            baseline_posture = max(posture_scores) if posture_scores else 1.0
            lowest_posture = min(posture_scores) if posture_scores else baseline_posture
            posture_drop_pct = (((baseline_posture - lowest_posture) / baseline_posture) * 100.0) if baseline_posture > 0 else 0.0

            base_delivery = 88.0
            # Factor in overall gaze ratio
            if gaze_ratio < 0.80:
                base_delivery -= min(25.0, (0.80 - gaze_ratio) * 50.0)
            elif gaze_ratio >= 0.88:
                base_delivery += min(8.0, (gaze_ratio - 0.88) * 35.0)

            # Factor in consecutive gaze loss duration
            if max_consecutive_gaze_loss >= 3.5:
                base_delivery -= min(16.0, (max_consecutive_gaze_loss - 3.0) * 2.5)

            # Factor in posture stability
            if posture_drop_pct > 15.0:
                base_delivery -= min(14.0, (posture_drop_pct - 15.0) * 0.5)

            # Penalize reading saccades (reading off notes/screen)
            if reading_saccade_flags >= 2:
                base_delivery -= min(12.0, reading_saccade_flags * 3.5)

            body_language_score = round(max(40.0, min(98.0, base_delivery)), 1)
        else:
            gaze_ratio = 0.85
            posture_drop_pct = 0.0
            body_language_score = None

        # ===================================================================
        # 4. Construct Calibrated Evaluation Envelope
        # ===================================================================
        rubric = question.get("rubric_breakdown", {"definition": 25, "mechanism": 35, "complexity": 20, "edge_cases": 20})
        rubric_scores = {
            "definition": round((rubric.get("definition", 25) / 100.0) * technical_depth_score, 1),
            "mechanism": round((rubric.get("mechanism", 35) / 100.0) * technical_depth_score, 1),
            "complexity": round((rubric.get("complexity", 20) / 100.0) * technical_depth_score, 1),
            "edge_cases": round((rubric.get("edge_cases", 20) / 100.0) * technical_depth_score, 1)
        }

        if technical_depth_score >= 90.0:
            grade = "S"
        elif technical_depth_score >= 80.0:
            grade = "A"
        elif technical_depth_score >= 70.0:
            grade = "B"
        elif technical_depth_score >= 55.0:
            grade = "C"
        else:
            grade = "D"

        delivery_penalties = []
        total_penalty = 0.0

        if max_consecutive_gaze_loss >= 4.0:
            ded = min(14.0, (max_consecutive_gaze_loss - 3.0) * 2.5)
            delivery_penalties.append({"type": "GAZE_DROP", "duration_sec": max_consecutive_gaze_loss, "deduction": ded})
            total_penalty += ded

        if posture_drop_pct > 20.0:
            ded = min(10.0, (posture_drop_pct - 20.0) * 0.4)
            delivery_penalties.append({"type": "POSTURE_COLLAPSE", "drop_percentage": posture_drop_pct, "deduction": ded})
            total_penalty += ded

        if (modulation_feedback and "monotone" in modulation_feedback.lower()) or (current_pitch_std < (user_baseline_std * 0.35) and len(pitches) > 10):
            delivery_penalties.append({"type": "MONOTONE_PITCH", "deduction": 5.0})
            total_penalty += 5.0

        if reading_saccade_flags >= 2:
            delivery_penalties.append({"type": "READING_SACCADE", "deduction": 8.0})
            total_penalty += 8.0

        return {
            "question_id": question.get("id", question_id),
            "question_title": question.get("title", "Technical Problem Solving"),
            "technical_score": technical_depth_score,
            "overall_score": technical_depth_score,  # Decoupled
            "grade": grade,
            "delivery_penalties": delivery_penalties,
            "total_penalty_deduction": round(total_penalty, 1),
            "rubric_breakdown": rubric_scores,
            "keyword_coverage": {
                "found_required": found_required,
                "missed_required": missed_required,
                "found_bonus": found_bonus,
                "required_coverage_ratio": round(req_coverage_ratio, 2),
                "bonus_coverage_ratio": round(bonus_coverage_ratio, 2)
            },
            "technical_depth": {
                "synergies_detected": depth_details,
                "depth_score": round(depth_score, 1)
            },
            "acoustic_prosodic_analysis": {
                "mean_pitch_f0": round(mean_pitch, 1),
                "pitch_std_hz": round(current_pitch_std, 1),
                "baseline_f0": round(user_baseline_f0, 1),
                "baseline_std": round(user_baseline_std, 1),
                "syllables_per_second": current_sps,
                "cadence_status": "Syllable-Timed Natural Rhythm" if current_sps >= 2.5 else "Deliberate Cadence",
                "cognitive_pauses_count": cognitive_pauses,
                "dead_air_pauses_count": dead_air_pauses,
                "modulation_feedback": modulation_feedback,
                "speech_clarity_score": speech_clarity_score
            },
            "visual_delivery_analysis": {
                "gaze_centered_percentage": int(round(gaze_ratio * 100)),
                "max_consecutive_gaze_loss_sec": round(max_consecutive_gaze_loss, 1),
                "posture_drop_percentage": round(posture_drop_pct, 1),
                "reading_saccades_detected": reading_saccade_flags,
                "body_language_score": body_language_score
            }
        }
