import os
import io
import wave
import uuid
import hashlib
from pathlib import Path
from django.conf import settings
from google import genai
from google.genai import types

# Complete Interviewer Accent Profiles
INTERVIEWER_PROFILES = {
    "kabir": {
        "name": "Kabir",
        "gender": "male",
        "accent_label": "IN English (North)",
        "sub_label": "Indian Male",
        "bcp47": "en-IN",
        "prompt_accent_instruction": "Speak in a natural, articulate North Indian English accent. Professional, calm, and encouraging senior interviewer persona.",
        "pitch": 0.95,
        "rate": 1.0,
    },
    "payal": {
        "name": "Payal",
        "gender": "female",
        "accent_label": "IN English (Standard)",
        "sub_label": "Indian Female",
        "bcp47": "en-IN",
        "prompt_accent_instruction": "Speak in a crisp, polished standard Indian English accent. Articulate, warm, clear, and professional female engineering leader.",
        "pitch": 1.1,
        "rate": 1.02,
    },
    "charlotte": {
        "name": "Charlotte",
        "gender": "female",
        "accent_label": "UK English (Standard)",
        "sub_label": "British Female",
        "bcp47": "en-GB",
        "prompt_accent_instruction": "Speak in a refined British Received Pronunciation (UK English) accent. Clear, measured, courteous, and intellectually sharp persona.",
        "pitch": 1.05,
        "rate": 0.98,
    },
    "john": {
        "name": "John",
        "gender": "male",
        "accent_label": "US English (General)",
        "sub_label": "American Male",
        "bcp47": "en-US",
        "prompt_accent_instruction": "Speak in a standard American English accent. Pragmatic, direct, engaging, and modern tech interviewer tone.",
        "pitch": 0.98,
        "rate": 1.05,
    },
    "sarah": {
        "name": "Sarah",
        "gender": "female",
        "accent_label": "US English (Standard)",
        "sub_label": "American Female",
        "bcp47": "en-US",
        "prompt_accent_instruction": "Speak in a friendly, articulate Standard American English accent. Insightful, analytical, structured Silicon Valley tech lead.",
        "pitch": 1.08,
        "rate": 1.0,
    },
    "kenji": {
        "name": "Kenji",
        "gender": "male",
        "accent_label": "JP English (Male)",
        "sub_label": "Japanese Male",
        "bcp47": "ja-JP",
        "prompt_accent_instruction": "Speak English with a subtle, polite, and measured Japanese accent cadence. Calm, thoughtful, disciplined engineering architect.",
        "pitch": 0.92,
        "rate": 0.95,
    },
    "aoi": {
        "name": "Aoi",
        "gender": "female",
        "accent_label": "JP English (Female)",
        "sub_label": "Japanese Female",
        "bcp47": "ja-JP",
        "prompt_accent_instruction": "Speak English with a gentle, structured Japanese accent cadence. Very clear, methodical, and welcoming persona.",
        "pitch": 1.15,
        "rate": 0.96,
    },
    "karthik": {
        "name": "Karthik",
        "gender": "male",
        "accent_label": "IN South English",
        "sub_label": "South Indian Male",
        "bcp47": "en-IN",
        "prompt_accent_instruction": "Speak in an energetic, rapid-thinking South Indian English accent. Sharp, technical, precise, and fast-paced systems engineer.",
        "pitch": 1.0,
        "rate": 1.08,
    },
    "vikram": {
        "name": "Vikram",
        "gender": "male",
        "accent_label": "IN Central English",
        "sub_label": "Central Indian Male",
        "bcp47": "en-IN",
        "prompt_accent_instruction": "Speak in a steady, resonant Central Indian English accent. Deep, authoritative, patient, and grounded senior engineering director.",
        "pitch": 0.9,
        "rate": 0.97,
    },
}

def pcm_to_wav(pcm_bytes, sample_rate=24000, channels=1, sample_width=2):
    """Convert raw 16-bit linear PCM audio to a valid WAV byte stream."""
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)
    buffer.seek(0)
    return buffer.read()


def synthesize_interviewer_speech(text, interviewer_name="Kabir"):
    """
    Synthesize speech for a designated interviewer in their authentic regional accent.
    Returns:
        dict: {
            "audio_url": str or None,
            "interviewer": str,
            "accent": str,
            "bcp47": str,
            "pitch": float,
            "rate": float,
            "format": "audio/wav",
            "cached": bool
        }
    """
    interviewer_key = interviewer_name.lower().strip()
    profile = INTERVIEWER_PROFILES.get(interviewer_key, INTERVIEWER_PROFILES["kabir"])

    # Unique cache key based on interviewer and text
    cache_dir = Path(settings.MEDIA_ROOT) / "audio_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    hash_digest = hashlib.md5(f"{profile['name']}_{text}".encode('utf-8')).hexdigest()
    wav_filename = f"tts_{profile['name'].lower()}_{hash_digest}.wav"
    wav_filepath = cache_dir / wav_filename
    relative_url = f"{settings.MEDIA_URL}audio_cache/{wav_filename}"

    if wav_filepath.exists() and wav_filepath.stat().st_size > 100:
        return {
            "success": True,
            "audio_url": relative_url,
            "interviewer": profile["name"],
            "accent": profile["accent_label"],
            "bcp47": profile["bcp47"],
            "pitch": profile["pitch"],
            "rate": profile["rate"],
            "cached": True,
        }

    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "success": False,
            "audio_url": None,
            "interviewer": profile["name"],
            "accent": profile["accent_label"],
            "bcp47": profile["bcp47"],
            "pitch": profile["pitch"],
            "rate": profile["rate"],
            "error": "GEMINI_API_KEY is not configured.",
        }

    try:
        client = genai.Client(api_key=api_key)
        tts_prompt = f"({profile['prompt_accent_instruction']}) {text}"

        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-tts',
            contents=tts_prompt,
            config={'response_modalities': ['AUDIO']}
        )

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    pcm_data = part.inline_data.data
                    wav_data = pcm_to_wav(pcm_data, sample_rate=24000, channels=1, sample_width=2)
                    with open(wav_filepath, 'wb') as f:
                        f.write(wav_data)
                    return {
                        "success": True,
                        "audio_url": relative_url,
                        "interviewer": profile["name"],
                        "accent": profile["accent_label"],
                        "bcp47": profile["bcp47"],
                        "pitch": profile["pitch"],
                        "rate": profile["rate"],
                        "cached": False,
                    }

        raise RuntimeError("No audio payload returned from Gemini TTS model.")

    except Exception as e:
        # Graceful fallback: return profile instructions for browser-level SpeechSynthesis
        return {
            "success": False,
            "audio_url": None,
            "interviewer": profile["name"],
            "accent": profile["accent_label"],
            "bcp47": profile["bcp47"],
            "pitch": profile["pitch"],
            "rate": profile["rate"],
            "fallback_to_client": True,
            "error": str(e),
        }

