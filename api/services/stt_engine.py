import os
import uuid
from pathlib import Path
from django.conf import settings
from google import genai
from ai_engine.glossary import TECHNICAL_TERMS, find_possible_corrections

SUPPORTED_AUDIO_TYPES = {
    ".wav": "audio/wav",
    ".mp3": "audio/mp3",
    ".m4a": "audio/mp4",
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
}

def transcribe_candidate_speech(audio_file_or_path, question_context=""):
    """
    Transcribe candidate's speech recording with dialect neutrality.
    Accepts:
        audio_file_or_path: file-like object, UploadedFile, or string path
        question_context: str
    Returns:
        dict: {
            "transcript": str,
            "corrections": list,
            "word_count": int,
            "model": str,
            "success": bool
        }
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    # Save to temporary path if UploadedFile or file-like object
    temp_dir = Path(settings.MEDIA_ROOT) / "candidate_recordings"
    temp_dir.mkdir(parents=True, exist_ok=True)

    if hasattr(audio_file_or_path, 'name') and hasattr(audio_file_or_path, 'read'):
        ext = Path(audio_file_or_path.name).suffix.lower() or ".webm"
        temp_path = temp_dir / f"rec_{uuid.uuid4().hex[:10]}{ext}"
        with open(temp_path, 'wb') as f:
            for chunk in audio_file_or_path.chunks():
                f.write(chunk)
    else:
        temp_path = Path(audio_file_or_path)

    mime_type = SUPPORTED_AUDIO_TYPES.get(temp_path.suffix.lower(), "audio/webm")

    # Step 1: Upload to Gemini Files API
    uploaded = client.files.upload(
        file=str(temp_path),
        config={"mime_type": mime_type}
    )

    try:
        # Prompt ensuring verbatim transcription and zero dialect penalties
        transcribe_prompt = (
            "You are a dialect-neutral, acoustic-fair speech transcription engine for a technical interview. "
            f"The candidate is answering the question: '{question_context}'. "
            "Transcribe the audio verbatim. Accurately transcribe technical terms, libraries, variables, algorithms, and acronyms "
            "regardless of Indian, British, American, Japanese, or any other regional cadence or accent. "
            "Do NOT paraphrase. Output the transcript only."
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[uploaded, transcribe_prompt]
        )

        transcript = (response.text or "").strip()

        # Step 2: Run technical glossary correction check
        corrections = find_possible_corrections(transcript)

        return {
            "success": True,
            "transcript": transcript,
            "corrections": corrections,
            "word_count": len(transcript.split()),
            "model": "gemini-2.5-flash",
            "audio_path": str(temp_path.relative_to(settings.BASE_DIR)) if temp_path.is_relative_to(settings.BASE_DIR) else str(temp_path)
        }

    finally:
        try:
            client.files.delete(name=uploaded.name)
        except Exception:
            pass
