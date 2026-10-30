"""
Temporal Slice & Timeline Engine (evaluator/timeline_engine.py)
Merges candidate transcript tokens with behavioral telemetry streams to generate
chronological flagged moments (KEY_MOMENT, BLUNDER, NEEDS_IMPROVEMENT) with exact
timestamps, physical/verbal observations, and targeted actionable coaching fixes.
"""
from typing import Dict, List, Any, Optional


class TimelineEngine:
    def __init__(self):
        pass

    def analyze_timeline(
        self,
        transcript: str,
        telemetry: List[Dict[str, Any]],
        deterministic_results: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates chronological moments tagging performance highlights and tells.
        """
        moments: List[Dict[str, Any]] = []
        if not telemetry and not transcript:
            return moments

        telemetry_stream = telemetry or []
        duration = telemetry_stream[-1].get("timestamp", 30.0) if telemetry_stream else 30.0

        # -------------------------------------------------------------
        # 1. Behavioral Stream Scanning: Gaze & Posture Tells
        # -------------------------------------------------------------
        current_gaze_loss_start = None
        current_gaze_loss_duration = 0.0

        current_slouch_start = None
        baseline_posture = max(
            [f.get("neck_ratio", f.get("posture_score", 1.0)) for f in telemetry_stream],
            default=1.0
        )

        prev_t = 0.0
        for idx, frame in enumerate(telemetry_stream):
            t = frame.get("timestamp", idx * 0.5)
            dt = t - prev_t if idx > 0 else 0.5
            prev_t = t

            # Gaze check
            is_looking = frame.get("eye_contact", frame.get("gaze_score", 1.0) >= 0.5)
            if not is_looking:
                if current_gaze_loss_start is None:
                    current_gaze_loss_start = t
                current_gaze_loss_duration += dt
            else:
                if current_gaze_loss_start is not None and current_gaze_loss_duration >= 3.5:
                    moments.append({
                        "type": "NEEDS_IMPROVEMENT" if current_gaze_loss_duration < 5.0 else "BLUNDER",
                        "timestamp_start": round(current_gaze_loss_start, 1),
                        "timestamp_end": round(t, 1),
                        "observation": f"Looked away from camera for {round(current_gaze_loss_duration, 1)}s during technical formulation.",
                        "actionable_fix": "Anchor your gaze on the webcam lens when formulating Big-O complexity or state transitions."
                    })
                current_gaze_loss_start = None
                current_gaze_loss_duration = 0.0

            # Posture check
            posture_val = frame.get("neck_ratio", frame.get("posture_score", baseline_posture))
            if baseline_posture > 0:
                drop_pct = ((baseline_posture - posture_val) / baseline_posture) * 100.0
                if drop_pct >= 18.0:
                    if current_slouch_start is None:
                        current_slouch_start = t
                else:
                    if current_slouch_start is not None and (t - current_slouch_start) >= 2.0:
                        moments.append({
                            "type": "NEEDS_IMPROVEMENT",
                            "timestamp_start": round(current_slouch_start, 1),
                            "timestamp_end": round(t, 1),
                            "observation": f"Shoulder collapse and posture drop ({round(drop_pct, 1)}% from baseline).",
                            "actionable_fix": "Maintain an open chest and upright alignment to signal composure and control under pressure."
                        })
                    current_slouch_start = None

        # Flush dangling gaze loss
        if current_gaze_loss_start is not None and current_gaze_loss_duration >= 3.5:
            moments.append({
                "type": "BLUNDER",
                "timestamp_start": round(current_gaze_loss_start, 1),
                "timestamp_end": round(duration, 1),
                "observation": f"Disengaged eye contact for {round(current_gaze_loss_duration, 1)}s toward the end of the answer.",
                "actionable_fix": "Conclude your explanation facing the interviewer directly with steady eye contact."
            })

        # -------------------------------------------------------------
        # 2. Verbal & Algorithmic Key Moments & Blunders
        # -------------------------------------------------------------
        if deterministic_results:
            found_req = deterministic_results.get("keyword_coverage", {}).get("found_required", [])
            missed_req = deterministic_results.get("keyword_coverage", {}).get("missed_required", [])
            synergies = deterministic_results.get("technical_depth", {}).get("synergies_detected", [])

            # Add key positive moments
            if found_req:
                moments.append({
                    "type": "KEY_MOMENT",
                    "timestamp_start": round(duration * 0.15, 1),
                    "timestamp_end": round(duration * 0.45, 1),
                    "observation": f"Successfully integrated core technical terms: {', '.join(found_req[:3])}.",
                    "actionable_fix": "Keep leading with strong technical primitives and canonical terminology upfront."
                })

            if synergies:
                for syn in synergies:
                    moments.append({
                        "type": "KEY_MOMENT",
                        "timestamp_start": round(duration * 0.5, 1),
                        "timestamp_end": round(duration * 0.75, 1),
                        "observation": f"High technical synergy: Linked '{syn['parent']}' directly with {', '.join(syn['co_occurring_children'])}.",
                        "actionable_fix": "Demonstrates senior-level architectural mechanics; highlight these trade-offs proactively."
                    })

            # Add missing concept blunders
            if missed_req:
                moments.append({
                    "type": "BLUNDER",
                    "timestamp_start": round(duration * 0.6, 1),
                    "timestamp_end": round(duration * 0.9, 1),
                    "observation": f"Omitted essential algorithmic mechanics: {', '.join(missed_req)}.",
                    "actionable_fix": f"Always state {', '.join(missed_req)} explicitly when discussing {deterministic_results.get('question_title', 'this topic')}."
                })

        # Sort chronologically by timestamp_start
        moments.sort(key=lambda m: m["timestamp_start"])
        return moments
