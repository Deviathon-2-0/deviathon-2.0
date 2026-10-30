import os
import io
import re
import wave
import uuid
import hashlib
import asyncio
import logging
import subprocess
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

# Try locating FFmpeg for Submind Audio DSP mastering
try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

# Try importing edge-tts for realistic human neural voices
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

# Try importing google.genai
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# 6 Focused, Iconic Evaluators with Unmistakable Authentic Accents
INTERVIEWER_PROFILES = {
    "kabir": {
        "name": "Kabir",
        "gender": "male",
        "region": "India (South)",
        "region_flag": "🇮🇳",
        "accent_label": "South Indian English (Male)",
        "sub_label": "Senior Systems Architect",
        "bcp47": "en-IN",
        "neural_voice": "en-IN-PrabhatNeural",
        "gemini_voice": "Puck",
        "pitch": 0.90,
        "rate": 1.0,
        "sample_intro": "Hello! I am Kabir. Let's delve into your technical architecture, data flow, and problem-solving strategy."
    },
    "payal": {
        "name": "Payal",
        "gender": "female",
        "region": "India (North)",
        "region_flag": "🇮🇳",
        "accent_label": "North Indian English (Female)",
        "sub_label": "VP of Engineering",
        "bcp47": "en-IN",
        "neural_voice": "en-IN-NeerjaExpressiveNeural",
        "gemini_voice": "Kore",
        "pitch": 1.15,
        "rate": 1.02,
        "sample_intro": "Hi there! I am Payal. I look forward to exploring your algorithmic trade-offs and scalable software patterns."
    },
    "john": {
        "name": "Arthur",
        "gender": "male",
        "region": "UK (London)",
        "region_flag": "🇬🇧",
        "accent_label": "UK English (Male)",
        "sub_label": "Principal Systems Lead",
        "bcp47": "en-GB",
        "neural_voice": "en-GB-ThomasNeural",
        "gemini_voice": "Puck",
        "pitch": 0.94,
        "rate": 0.98,
        "sample_intro": "Good day. I am Arthur. We shall examine system concurrency, latency guarantees, and resilience under load."
    },
    "arthur": {
        "name": "Arthur",
        "gender": "male",
        "region": "UK (London)",
        "region_flag": "🇬🇧",
        "accent_label": "UK English (Male)",
        "sub_label": "Principal Systems Lead",
        "bcp47": "en-GB",
        "neural_voice": "en-GB-ThomasNeural",
        "gemini_voice": "Puck",
        "pitch": 0.94,
        "rate": 0.98,
        "sample_intro": "Good day. I am Arthur. We shall examine system concurrency, latency guarantees, and resilience under load."
    },
    "david": {
        "name": "David",
        "gender": "male",
        "region": "North America",
        "region_flag": "🇺🇸",
        "accent_label": "US English (Male)",
        "sub_label": "Silicon Valley Tech Lead",
        "bcp47": "en-US",
        "neural_voice": "en-US-ChristopherNeural",
        "gemini_voice": "Puck",
        "pitch": 0.92,
        "rate": 1.04,
        "sample_intro": "Hey! I am David. Excited to dive into your implementation and discuss how you tackle bottlenecks at scale."
    },
    "sarah": {
        "name": "David",
        "gender": "male",
        "region": "North America",
        "region_flag": "🇺🇸",
        "accent_label": "US English (Male)",
        "sub_label": "Silicon Valley Tech Lead",
        "bcp47": "en-US",
        "neural_voice": "en-US-ChristopherNeural",
        "gemini_voice": "Puck",
        "pitch": 0.92,
        "rate": 1.04,
        "sample_intro": "Hey! I am David. Excited to dive into your implementation and discuss how you tackle bottlenecks at scale."
    },
    "charlotte": {
        "name": "Charlotte",
        "gender": "female",
        "region": "Scotland (UK)",
        "region_flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
        "accent_label": "Scottish English (Female)",
        "sub_label": "Principal Infrastructure Lead",
        "bcp47": "en-GB",
        "neural_voice": "en-GB-MaisieNeural",
        "gemini_voice": "Aoede",
        "pitch": 1.12,
        "rate": 1.00,
        "sample_intro": "Hello there! I am Charlotte. Let us examine your fault tolerance, algorithmic constraints, and edge cases."
    },
    "kenji": {
        "name": "Yuki",
        "gender": "female",
        "region": "Japan (Tokyo)",
        "region_flag": "🇯🇵",
        "accent_label": "Japanese English (Female)",
        "sub_label": "Robotics & AI Systems Lead",
        "bcp47": "ja-JP",
        "neural_voice": "ja-JP-NanamiNeural",
        "gemini_voice": "Aoede",
        "pitch": 1.10,
        "rate": 0.95,
        "sample_intro": "Konnichiwa! I am Yuki. Please walk through your architectural assumptions and step-by-step logic with clarity."
    },
    "yuki": {
        "name": "Yuki",
        "gender": "female",
        "region": "Japan (Tokyo)",
        "region_flag": "🇯🇵",
        "accent_label": "Japanese English (Female)",
        "sub_label": "Robotics & AI Systems Lead",
        "bcp47": "ja-JP",
        "neural_voice": "ja-JP-NanamiNeural",
        "gemini_voice": "Aoede",
        "pitch": 1.10,
        "rate": 0.95,
        "sample_intro": "Konnichiwa! I am Yuki. Please walk through your architectural assumptions and step-by-step logic with clarity."
    }
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


def sanitize_interview_text(text: str) -> str:
    """
    Cleans raw problem prompts, stripping XML/SSML declarations, HTML tags, Markdown artifacts,
    code blocks, editorial constraints, test cases, and symbol glitches so that
    the speech synthesis engine produces natural, conversational speech without reading
    code tokens like '=', '<=', '<div>', 'Input:', or '.' as 'stop point' and without reading
    SSML/XML headers aloud.
    """
    if not text:
        return ""
    
    # 0. Strip XML/SSML declarations and speech tags completely
    clean = re.sub(r'<\?xml[^>]*\?>', ' ', text, flags=re.IGNORECASE)
    clean = re.sub(r'<\/?(?:speak|voice|prosody|mstts:[^>]+|audio|break|emphasis|lang|phoneme|say-as|sub|p|s)[^>]*>', ' ', clean, flags=re.IGNORECASE)
    
    # 1. Strip HTML tags completely
    clean = re.sub(r'<[^>]+>', ' ', clean)
    
    # 2. Strip code blocks & inline code
    clean = re.sub(r'```[\s\S]*?```', ' ', clean)
    clean = re.sub(r'`[^`]*`', ' ', clean)
    
    # 3. Strip editorial sections like Example 1, Input:, Output:, Constraints:
    cut_match = re.search(r'(?i)\b(example\s*\d*|input\s*:|output\s*:|constraints?\s*:|sample\s+input|test\s*cases?)\b', clean)
    if cut_match:
        clean = clean[:cut_match.start()]
    
    # 4. Strip mathematical comparison operators and code symbols
    clean = re.sub(r'[*_#~\[\]()\\<>=|{}]', ' ', clean)
    clean = re.sub(r'&(?:[a-z\d]+|#\d+|#x[a-f\d]+);', ' ', clean)
    clean = re.sub(r'https?://\S+', '', clean)
    
    # 5. Fix standalone dots, multiple dots, and punctuation spacing
    clean = re.sub(r'\s+([.,?!:;])', r'\1', clean)
    clean = re.sub(r'\.{2,}', '.', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    # 6. Ensure sentences don't have stray periods inside identifiers (e.g. s.length)
    clean = re.sub(r'\b([a-zA-Z])\.([a-zA-Z])\b', r'\1 \2', clean)
    
    return clean


def build_emotion_ssml(text, voice_name, gender="male", pacing_factor=1.0):
    """
    Build clean, natural human SSML without symbol artifacts or 'stop point' glitching:
    - Strips all HTML/code/editorial noise via sanitize_interview_text
    - Escapes XML characters safely
    - Applies natural prosody rate without breaking voice synthesis
    """
    clean = sanitize_interview_text(text)
    if not clean:
        clean = "Please walk me through your technical approach and how you would design an optimal solution."

    # Escape XML characters safely
    clean = clean.replace('&', '&amp;')
    clean = clean.replace('<', '&lt;')
    clean = clean.replace('>', '&gt;')
    clean = clean.replace('"', '&quot;')
    clean = clean.replace("'", '&apos;')

    percent_delta = int((pacing_factor - 1.0) * 100)
    rate_str = f"+{percent_delta}%" if percent_delta >= 0 else f"{percent_delta}%"

    ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'>
<voice name='{voice_name}'>
<prosody rate='{rate_str}'>
{clean}
</prosody>
</voice>
</speak>"""
    return ssml


def apply_submind_audio_mastering(raw_path, output_path):
    """
    Submind Studio Audio DSP Mastering Chain:
    - High-pass 80 Hz: Removes sub-bass desk thump & muddy resonance
    - Presence clarity boost at 3.4 kHz (+3.8 dB): Makes speech crisp and operative tokens intelligible
    - De-box notch at 300 Hz (-1.5 dB)
    - Broadcast vocal compander (smooth leveling)
    - EBU R128 loudness normalization for punchy, crystal-clear sound
    """
    if not os.path.exists(raw_path) or os.path.getsize(raw_path) < 100:
        return False

    dsp_filter = (
        'highpass=f=80,'
        'equalizer=f=3400:t=q:w=1.4:g=3.8,'
        'equalizer=f=300:t=q:w=1.2:g=-1.5,'
        'compand=attacks=0.02:decays=0.15:points=-80/-80|-24/-12|-6/-3|0/0,'
        'loudnorm=I=-16:TP=-1.5:LRA=7'
    )
    cmd = [
        FFMPEG_EXE, '-y',
        '-i', str(raw_path),
        '-af', dsp_filter,
        '-c:a', 'libmp3lame',
        '-b:a', '192k',
        str(output_path)
    ]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=12)
        if p.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 500:
            return True
    except Exception as e:
        logger.warning(f"Submind DSP mastering fallback: {e}")
    return False


async def _generate_edge_tts(clean_text, voice_name, output_path, rate_str="+0%"):
    """Generate audio using Edge TTS neural human voice with plain text (Edge TTS wraps SSML internally)."""
    communicate = edge_tts.Communicate(clean_text, voice_name, rate=rate_str)
    await communicate.save(output_path)


def synthesize_interviewer_speech(text, interviewer_name="Kabir", pacing="1.0"):
    text = sanitize_interview_text(text)
    """
    Synthesize high-fidelity human speech for a designated interviewer.
    Prioritizes ultra-realistic Neural Voices (Edge TTS) with authentic gender & accent,
    falling back to Gemini TTS or browser-level speech profiles.
    """
    interviewer_key = interviewer_name.lower().strip()
    profile = INTERVIEWER_PROFILES.get(interviewer_key, INTERVIEWER_PROFILES["kabir"])

    # Pacing to Edge TTS rate string
    try:
        pacing_factor = float(pacing)
    except (ValueError, TypeError):
        pacing_factor = 1.0

    percent_delta = int((pacing_factor - 1.0) * 100)
    rate_str = f"+{percent_delta}%" if percent_delta >= 0 else f"{percent_delta}%"

    # Audio Cache setup
    cache_dir = Path(settings.MEDIA_ROOT) / "audio_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    hash_digest = hashlib.md5(f"{profile['name']}_{profile['gender']}_{rate_str}_{text}".encode('utf-8')).hexdigest()
    mp3_filename = f"tts_{profile['name'].lower()}_{hash_digest}.mp3"
    mp3_filepath = cache_dir / mp3_filename
    relative_url = f"{settings.MEDIA_URL}audio_cache/{mp3_filename}"

    # Return cached audio if present
    if mp3_filepath.exists() and mp3_filepath.stat().st_size > 1000:
        return {
            "success": True,
            "audio_url": relative_url,
            "interviewer": profile["name"],
            "gender": profile["gender"],
            "accent": profile["accent_label"],
            "region": profile["region"],
            "region_flag": profile["region_flag"],
            "bcp47": profile["bcp47"],
            "pitch": profile["pitch"],
            "rate": pacing_factor,
            "format": "audio/mp3",
            "cached": True,
        }

    # 1. Primary: Neural Edge TTS with Clean Sanitized Text & Submind Audio DSP
    if HAS_EDGE_TTS:
        try:
            voice_name = profile.get("neural_voice", "en-US-JennyNeural")
            clean_text = sanitize_interview_text(text)
            if not clean_text:
                clean_text = "Please walk me through your technical approach and how you would design an optimal solution."
            raw_tmp = cache_dir / f"raw_{mp3_filename}"
            asyncio.run(_generate_edge_tts(clean_text, voice_name, str(raw_tmp), rate_str=rate_str))
            
            if raw_tmp.exists() and raw_tmp.stat().st_size > 500:
                mastered = apply_submind_audio_mastering(raw_tmp, mp3_filepath)
                if not mastered or not mp3_filepath.exists():
                    raw_tmp.replace(mp3_filepath)
                else:
                    if raw_tmp.exists():
                        raw_tmp.unlink(missing_ok=True)
            
            if mp3_filepath.exists() and mp3_filepath.stat().st_size > 500:
                return {
                    "success": True,
                    "audio_url": relative_url,
                    "interviewer": profile["name"],
                    "gender": profile["gender"],
                    "accent": profile["accent_label"],
                    "region": profile["region"],
                    "region_flag": profile["region_flag"],
                    "bcp47": profile["bcp47"],
                    "pitch": profile["pitch"],
                    "rate": pacing_factor,
                    "format": "audio/mp3",
                    "cached": False,
                }
        except Exception as edge_err:
            pass  # Fall through to Gemini or browser fallback

    # 2. Secondary: Gemini TTS
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY")
    if HAS_GENAI and api_key:
        try:
            client = genai.Client(api_key=api_key)
            gender_prompt = "deep authoritative male" if profile["gender"] == "male" else "clear articulate female"
            tts_prompt = f"(Speak as a {gender_prompt} professional interviewer with a natural {profile['accent_label']} accent) {text}"

            response = client.models.generate_content(
                model='gemini-2.5-flash-preview-tts',
                contents=tts_prompt,
                config={
                    'response_modalities': ['AUDIO'],
                    'speech_config': {
                        'voice_config': {
                            'prebuilt_voice_config': {
                                'voice_name': profile.get('gemini_voice', 'Puck')
                            }
                        }
                    }
                }
            )

            wav_filename = f"tts_{profile['name'].lower()}_{hash_digest}.wav"
            wav_filepath = cache_dir / wav_filename
            wav_relative_url = f"{settings.MEDIA_URL}audio_cache/{wav_filename}"

            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        pcm_data = part.inline_data.data
                        wav_data = pcm_to_wav(pcm_data, sample_rate=24000, channels=1, sample_width=2)
                        with open(wav_filepath, 'wb') as f:
                            f.write(wav_data)
                        return {
                            "success": True,
                            "audio_url": wav_relative_url,
                            "interviewer": profile["name"],
                            "gender": profile["gender"],
                            "accent": profile["accent_label"],
                            "region": profile["region"],
                            "region_flag": profile["region_flag"],
                            "bcp47": profile["bcp47"],
                            "pitch": profile["pitch"],
                            "rate": pacing_factor,
                            "format": "audio/wav",
                            "cached": False,
                        }
        except Exception:
            pass

    # 3. Client Fallback: Provide detailed gender, pitch, and accent specification
    return {
        "success": False,
        "audio_url": None,
        "interviewer": profile["name"],
        "gender": profile["gender"],
        "accent": profile["accent_label"],
        "region": profile["region"],
        "region_flag": profile["region_flag"],
        "bcp47": profile["bcp47"],
        "pitch": profile["pitch"],
        "rate": pacing_factor,
        "sample_intro": profile.get("sample_intro", ""),
        "fallback_to_client": True,
        "error": "Generated via client-side human neural voice model."
    }
