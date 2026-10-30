"""
Deterministic Rubric & Behavioral Scorer (evaluator/deterministic_scorer.py)
Performs Tier-1 in-memory deterministic evaluation matching normalized transcripts
against question registries, evaluating keyword coverage, technical depth,
and behavioral delivery penalties (gaze drops, pitch monotone, slouching, lip-sync).
"""
import re
import math
from typing import Dict, List, Any, Optional, Tuple
from evaluator.catalog import INTERVIEW_QUESTION_REGISTRY


class DeterministicScorer:
    def __init__(self, question_registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self.registry = question_registry or INTERVIEW_QUESTION_REGISTRY

    def evaluate(
        self,
        question_id: str,
        normalized_transcript: str,
        telemetry: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Runs Tier-1 deterministic evaluation against rubric and behavioral telemetry.
        """
        question = self.registry.get(question_id)
        if not question:
            # Fallback to general technical question rubric
            question = self.registry.get("default_general", {
                "id": question_id,
                "title": "Technical Problem Solving",
                "difficulty": "Medium",
                "required_keywords": ["time_complexity", "space_complexity", "O(1)"],
                "bonus_keywords": ["tradeoffs", "edge_cases"],
                "rubric_breakdown": {"definition": 25, "mechanism": 35, "complexity": 25, "edge_cases": 15},
                "child_concept_groups": []
            })

        transcript_lower = normalized_transcript.lower()
        telemetry_stream = telemetry or []

        # -------------------------------------------------------------
        # 1. Keyword Coverage Analysis
        # -------------------------------------------------------------
        required_kw = question.get("required_keywords", [])
        bonus_kw = question.get("bonus_keywords", [])

        found_required = []
        missed_required = []
        for kw in required_kw:
            # Match canonical kw or with space instead of underscore
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

        # -------------------------------------------------------------
        # 2. Technical Depth & Synergy Analysis (Child Concept Co-occurrence)
        # -------------------------------------------------------------
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

        # Technical depth contributes up to 25 points
        if child_groups:
            depth_score = (depth_hits / len(child_groups)) * 25.0
        else:
            # Generic technical word density check
            tech_tokens = ["time_complexity", "space_complexity", "O(1)", "O(n)", "memory", "optimal", "constraint"]
            hits = sum(1 for t in tech_tokens if t in transcript_lower)
            depth_score = min(25.0, hits * 5.0)

        raw_technical_score = min(100.0, keyword_score + depth_score)

        # -------------------------------------------------------------
        # 3. Delivery Penalties from Behavioral Stream (Telemetry)
        # -------------------------------------------------------------
        penalties = []
        total_penalty = 0.0

        if telemetry_stream:
            # (a) Eye contact drop > 4 consecutive seconds
            max_consecutive_gaze_loss = 0.0
            current_gaze_loss = 0.0
            prev_t = None
            for frame in telemetry_stream:
                t = frame.get("timestamp", 0.0)
                dt = (t - prev_t) if prev_t is not None else 0.2
                prev_t = t
                is_looking = frame.get("eye_contact", frame.get("gaze_score", 1.0) >= 0.5)
                if not is_looking:
                    current_gaze_loss += max(dt, 0.1)
                    if current_gaze_loss > max_consecutive_gaze_loss:
                        max_consecutive_gaze_loss = current_gaze_loss
                else:
                    current_gaze_loss = 0.0

            if max_consecutive_gaze_loss >= 4.0:
                deduction = min(12.0, 5.0 + (max_consecutive_gaze_loss - 4.0) * 1.5)
                penalties.append({
                    "type": "GAZE_DROP",
                    "deduction": round(deduction, 1),
                    "reason": f"Lost continuous eye contact for {round(max_consecutive_gaze_loss, 1)}s (threshold: 4.0s)"
                })
                total_penalty += deduction

            # (b) Monotone Pitch Streaks (pitch std dev < 6.5 Hz across speaking segments)
            pitches = [
                frame.get("pitch_hz", frame.get("pitch", 0.0))
                for frame in telemetry_stream
                if frame.get("pitch_hz", frame.get("pitch", 0.0)) > 60.0
            ]
            if len(pitches) >= 5:
                mean_p = sum(pitches) / len(pitches)
                variance = sum((p - mean_p) ** 2 for p in pitches) / len(pitches)
                pitch_std = math.sqrt(variance)
                if pitch_std < 6.5:
                    penalties.append({
                        "type": "MONOTONE_PITCH",
                        "deduction": 6.0,
                        "reason": f"Monotone vocal delivery detected (Pitch std dev {round(pitch_std, 1)} Hz < 6.5 Hz)"
                    })
                    total_penalty += 6.0

            # (c) Slouching / Hunched posture drops (>18% neck length or posture drop)
            posture_vals = [
                frame.get("neck_ratio", frame.get("posture_score", 1.0))
                for frame in telemetry_stream
                if "neck_ratio" in frame or "posture_score" in frame
            ]
            if posture_vals:
                baseline_posture = max(posture_vals)
                lowest_posture = min(posture_vals)
                if baseline_posture > 0:
                    posture_drop_pct = ((baseline_posture - lowest_posture) / baseline_posture) * 100.0
                    if posture_drop_pct > 18.0:
                        deduction = min(10.0, 4.0 + (posture_drop_pct - 18.0) * 0.3)
                        penalties.append({
                            "type": "POSTURE_COLLAPSE",
                            "deduction": round(deduction, 1),
                            "reason": f"Hunched posture detected ({round(posture_drop_pct, 1)}% drop from baseline, threshold: 18%)"
                        })
                        total_penalty += deduction

            # (d) AV Lip-Sync Mismatch Flags
            lip_sync_mismatches = sum(
                1 for frame in telemetry_stream
                if frame.get("lip_sync_mismatch", False) or frame.get("av_sync_error", False)
            )
            if lip_sync_mismatches >= 3:
                penalties.append({
                    "type": "LIP_SYNC_MISMATCH",
                    "deduction": 5.0,
                    "reason": f"AV lip-sync mismatch detected across {lip_sync_mismatches} frames"
                })
                total_penalty += 5.0

        # -------------------------------------------------------------
        # 4. Final Score & Rubric Dimensions Computation
        # -------------------------------------------------------------
        final_score = max(0.0, min(100.0, raw_technical_score - total_penalty))
        final_score = round(final_score, 1)

        rubric = question.get("rubric_breakdown", {"definition": 25, "mechanism": 35, "complexity": 20, "edge_cases": 20})
        rubric_scores = {
            "definition": round((rubric.get("definition", 25) / 100.0) * final_score, 1),
            "mechanism": round((rubric.get("mechanism", 35) / 100.0) * final_score, 1),
            "complexity": round((rubric.get("complexity", 20) / 100.0) * final_score, 1),
            "edge_cases": round((rubric.get("edge_cases", 20) / 100.0) * final_score, 1)
        }

        # Assign letter grade
        if final_score >= 90:
            grade = "S"
        elif final_score >= 80:
            grade = "A"
        elif final_score >= 70:
            grade = "B"
        elif final_score >= 55:
            grade = "C"
        else:
            grade = "D"

        word_count = len(normalized_transcript.split())
        # Ambiguity Flag: Triggers Tier-2 Gemini synthesis/fallback if score is borderline or response is short
        is_ambiguous = (45.0 <= final_score <= 68.0) or (word_count < 15) or (len(found_required) == 0 and word_count > 25)

        return {
            "question_id": question.get("id", question_id),
            "question_title": question.get("title", ""),
            "overall_score": final_score,
            "raw_technical_score": round(raw_technical_score, 1),
            "grade": grade,
            "keyword_coverage": {
                "required_coverage_ratio": round(req_coverage_ratio, 2),
                "bonus_coverage_ratio": round(bonus_coverage_ratio, 2),
                "found_required": found_required,
                "missed_required": missed_required,
                "found_bonus": found_bonus
            },
            "technical_depth": {
                "depth_score": round(depth_score, 1),
                "synergies_detected": depth_details
            },
            "delivery_penalties": penalties,
            "total_penalty_deduction": round(total_penalty, 1),
            "rubric_breakdown": rubric_scores,
            "word_count": word_count,
            "ambiguity_flag": is_ambiguous
        }
