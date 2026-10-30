/**
 * IMAIRA+ Speech Player (TTS)
 * 
 * Provides hybrid text-to-speech audio playback:
 * 1. Primary: Browser-native Web Speech API (SpeechSynthesis) configured for Indian English (en-IN).
 * 2. Fallback: Backend TTS endpoint (/api/speech/synthesize) streamed via HTML5 Audio.
 */

class SpeechPlayer {
  constructor(options = {}) {
    this.api = options.api || window.speechApi;
    this.language = options.language || "en-IN";
    this.rate = options.rate || 0.95; // Slightly slower, crisp cadence for interview clarity
    this.pitch = options.pitch || 1.0;
    this.isMuted = false;
    this.isPlaying = false;
    this.currentAudio = null;
    this.selectedVoice = null;

    this.onStart = options.onStart || (() => {});
    this.onEnd = options.onEnd || (() => {});
    this.onError = options.onError || (() => {});

    this.hasWebSpeech = "speechSynthesis" in window;

    if (this.hasWebSpeech) {
      this._initVoices();
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = () => this._initVoices();
      }
    }
  }

  /**
   * Find the most appropriate Indian English or natural voice.
   */
  _initVoices() {
    if (!this.hasWebSpeech) return;
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return;

    // Prefer en-IN voices (e.g. Google Indian English, Rishi, Veena, Heera, etc.)
    const inVoice = voices.find(v => v.lang.includes("en-IN") || v.lang.includes("en_IN"));
    // Secondary: en-GB / en-US natural voices
    const naturalVoice = voices.find(v => (v.name.includes("Natural") || v.name.includes("Google")) && v.lang.startsWith("en"));
    // Fallback: any English voice
    const fallbackVoice = voices.find(v => v.lang.startsWith("en"));

    this.selectedVoice = inVoice || naturalVoice || fallbackVoice || voices[0];
    console.log("[SpeechPlayer] Selected TTS voice:", this.selectedVoice ? `${this.selectedVoice.name} (${this.selectedVoice.lang})` : "Default");
  }

  /**
   * Speak the given text.
   * Cancels any ongoing playback first.
   * 
   * @param {string} text - Question or prompt text
   * @param {Object} options - Custom overrides { onStart, onEnd, rate, pitch }
   */
  async speak(text, options = {}) {
    this.stop();

    if (this.isMuted) {
      console.log("[SpeechPlayer] Playback suppressed (muted)");
      return;
    }

    if (!text || typeof text !== "string" || text.trim().length === 0) {
      return;
    }

    const cleanText = text.replace(/^["']|["']$/g, "").trim();

    const onStart = options.onStart || this.onStart;
    const onEnd = options.onEnd || this.onEnd;
    const onError = options.onError || this.onError;

    // Try Web Speech API first
    if (this.hasWebSpeech) {
      try {
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = options.language || this.language;
        utterance.rate = options.rate || this.rate;
        utterance.pitch = options.pitch || this.pitch;

        if (this.selectedVoice) {
          utterance.voice = this.selectedVoice;
        }

        utterance.onstart = () => {
          this.isPlaying = true;
          onStart();
        };

        utterance.onend = () => {
          this.isPlaying = false;
          onEnd();
        };

        utterance.onerror = (e) => {
          console.warn("[SpeechPlayer] Web Speech error, falling back to server TTS:", e);
          this._fallbackBackendSpeak(cleanText, { onStart, onEnd, onError });
        };

        window.speechSynthesis.speak(utterance);
        return;
      } catch (err) {
        console.warn("[SpeechPlayer] Web Speech exception, falling back:", err);
      }
    }

    // Fallback to Backend TTS API
    await this._fallbackBackendSpeak(cleanText, { onStart, onEnd, onError });
  }

  /**
   * Play speech via backend TTS audio stream.
   */
  async _fallbackBackendSpeak(text, { onStart, onEnd, onError }) {
    if (!this.api) {
      console.error("[SpeechPlayer] No speech API configured for fallback synthesis.");
      onError(new Error("No TTS provider available"));
      return;
    }

    try {
      this.isPlaying = true;
      onStart();

      const blob = await this.api.synthesizeSpeech(text, { language: this.language });
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      this.currentAudio = audio;

      audio.onended = () => {
        this.isPlaying = false;
        URL.revokeObjectURL(audioUrl);
        this.currentAudio = null;
        onEnd();
      };

      audio.onerror = (err) => {
        this.isPlaying = false;
        URL.revokeObjectURL(audioUrl);
        this.currentAudio = null;
        onError(err);
      };

      await audio.play();
    } catch (err) {
      this.isPlaying = false;
      console.error("[SpeechPlayer] Backend synthesis failed:", err);
      onError(err);
    }
  }

  /**
   * Stop active speech immediately.
   */
  stop() {
    this.isPlaying = false;
    if (this.hasWebSpeech && window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
    this.onEnd();
  }

  /**
   * Toggle mute state.
   */
  toggleMute() {
    this.isMuted = !this.isMuted;
    if (this.isMuted) {
      this.stop();
    }
    return this.isMuted;
  }
}

// Global instance attached to window
window.SpeechPlayer = SpeechPlayer;
window.speechPlayer = new SpeechPlayer();
