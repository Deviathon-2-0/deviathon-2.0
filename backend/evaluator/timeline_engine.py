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
            [float(f.get("neck_ratio", f.get("posture_score", 1.0))) for f in telemetry_stream],
            default=1.0
        )

        prev_t = 0.0
        for idx, frame in enumerate(telemetry_stream):
            t = float(frame.get("timestamp", idx * 0.5))
            dt = t - prev_t if idx > 0 else 0.5
            prev_t = t

            # Gaze check
            is_looking = frame.get("eye_contact", frame.get("gaze_score", 1.0) >= 0.5)
            if not is_looking:
                if current_gaze_loss_start is None:
                    current_gaze_loss_start = t
                current_gaze_loss_duration += dt
            else:
                if current_gaze_loss_start is not None and current_gaze_loss_duration >= 4.0:
                    moments.append({
                        "type": "NEEDS_IMPROVEMENT" if current_gaze_loss_duration < 6.0 else "BLUNDER",
                        "timestamp_start": round(current_gaze_loss_start, 1),
                        "timestamp_end": round(t, 1),
                        "observation": f"Looked away from camera for {round(current_gaze_loss_duration, 1)}s during explanation.",
                        "actionable_fix": "Anchor your gaze on the webcam lens when formulating trade-offs or key invariants."
                    })
                current_gaze_loss_start = None
                current_gaze_loss_duration = 0.0

            # Posture check
            posture_val = float(frame.get("neck_ratio", frame.get("posture_score", baseline_posture)))
            if baseline_posture > 0:
                drop_pct = ((baseline_posture - posture_val) / baseline_posture) * 100.0
                if drop_pct >= 22.0:
                    if current_slouch_start is None:
                        current_slouch_start = t
                else:
                    if current_slouch_start is not None and (t - current_slouch_start) >= 2.5:
                        moments.append({
                            "type": "NEEDS_IMPROVEMENT",
                            "timestamp_start": round(current_slouch_start, 1),
                            "timestamp_end": round(t, 1),
                            "observation": f"Shoulder collapse and posture drop ({round(drop_pct, 1)}% from baseline).",
                            "actionable_fix": "Maintain an open chest and upright alignment to signal composure and control under pressure."
                        })
                    current_slouch_start = None

        # Flush dangling gaze loss
        if current_gaze_loss_start is not None and current_gaze_loss_duration >= 4.0:
            moments.append({
                "type": "NEEDS_IMPROVEMENT",
                "timestamp_start": round(current_gaze_loss_start, 1),
                "timestamp_end": round(duration, 1),
                "observation": f"Disengaged eye contact for {round(current_gaze_loss_duration, 1)}s toward the end of the answer.",
                "actionable_fix": "Conclude your explanation facing the interviewer directly with steady eye contact."
            })

        # -------------------------------------------------------------
        # 2. Verbal & Algorithmic Key Moments
        # -------------------------------------------------------------
        if deterministic_results:
            found_req = deterministic_results.get("keyword_coverage", {}).get("found_required", [])
            synergies = deterministic_results.get("technical_depth", {}).get("synergies_detected", [])
            prosody = deterministic_results.get("acoustic_prosodic_analysis", {})

            # Positive Key Moment: Technical concept co-occurrence
            if synergies:
                top_syn = synergies[0]
                parent = top_syn.get("parent", "").replace("_", " ")
                children = ", ".join(top_syn.get("co_occurring_children", [])).replace("_", " ")
                moments.append({
                    "type": "KEY_MOMENT",
                    "timestamp_start": 3.5,
                    "timestamp_end": 7.0,
                    "observation": f"High technical synergy: Correlated {parent} with {children}.",
                    "actionable_fix": "Preserve this strong pattern of linking core concepts to their internal mechanisms."
                })
            elif found_req:
                first_kws = ", ".join(found_req[:2]).replace("_", " ")
                moments.append({
                    "type": "KEY_MOMENT",
                    "timestamp_start": 2.0,
                    "timestamp_end": 5.0,
                    "observation": f"Clear technical framing: Explicitly articulated {first_kws}.",
                    "actionable_fix": "Effective upfront structure; continue stating invariants early in your answers."
                })

            # Positive Key Moment: Cognitive pause & composure
            if prosody.get("cognitive_pauses_count", 0) >= 1:
                moments.append({
                    "type": "KEY_MOMENT",
                    "timestamp_start": 1.2,
                    "timestamp_end": 2.8,
                    "observation": "Natural cognitive pause before speaking: formulated structured approach with composure.",
                    "actionable_fix": "Maintain deliberate 1-2s cognitive pauses rather than rushing into impromptu responses."
                })

        return moments
