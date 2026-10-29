import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from ai_engine.glossary import TECHNICAL_TERMS

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Check your .env file.")

client = genai.Client(api_key=API_KEY)

TRANSCRIPTION_MODEL = "gemini-3.5-transcribe"

SUPPORTED_AUDIO_TYPES = {
    ".wav": "audio/wav",
    ".mp3": "audio/mp3",
    ".m4a": "audio/mp4",
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
}


def transcribe_audio(audio_path, question=None, use_custom_vocabulary=True):
    """Transcribe an interview recording without rewriting the answer."""

    audio_path = Path(audio_path)

    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    mime_type = SUPPORTED_AUDIO_TYPES.get(audio_path.suffix.lower())

    if mime_type is None:
        raise ValueError(f"Unsupported audio format: {audio_path.suffix}")

    audio_file = client.files.upload(
        file=str(audio_path),
        config={"mime_type": mime_type},
    )

    try:
        transcription_config = {
            "language_codes": ["en-IN"],
            "mode": "verbatim",
        }

        if use_custom_vocabulary:
            transcription_config["custom_vocabulary"] = TECHNICAL_TERMS[:100]

        interaction = client.interactions.create(
            model=TRANSCRIPTION_MODEL,
            input=[
                {
                    "type": "audio",
                    "uri": audio_file.uri,
                    "mime_type": mime_type,
                }
            ],
            generation_config={
                "transcription_config": transcription_config
            },
        )

        transcript = (interaction.output_text or "").strip()

        if not transcript:
            raise RuntimeError("The transcription model returned an empty transcript.")

        return {
            "transcript": transcript,
            "model": TRANSCRIPTION_MODEL,
            "language_hint": "en-IN",
            "custom_vocabulary_used": use_custom_vocabulary,
            "question": question,
        }

    finally:
        try:
            client.files.delete(name=audio_file.name)
        except Exception as error:
            print(
                "WARNING: Could not delete uploaded audio. "
                f"Manual cleanup may be required: {error}"
            )