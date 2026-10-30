/**
 * Zero-Lag Client-Side Speech Recognition Handler (Tier 1)
 * frontend/js/stt_handler.js
 * 
 * Configures the native browser Web Speech API (webkitSpeechRecognition) for:
 * - Instantaneous 0ms real-time interim speech rendering
 * - Regional accent-tuned acoustic recognition (default: 'en-IN')
 * - Continuous listening with graceful reconnect on silence or pause
 * - Anti-overlap gate: cancels TTS audio when candidate begins speaking
 */

class InstantSTTHandler {
  constructor(options = {}) {
    this.lang = options.lang || 'en-IN';
    this.continuous = options.continuous !== false;
    this.interimResults = options.interimResults !== false;
    
    this.recognition = null;
    this.isListening = false;
    this.accumulatedTranscript = '';
    this.interimTranscript = '';
    
    this.onInterim = options.onInterim || (() => {});
    this.onFinal = options.onFinal || (() => {});
    this.onError = options.onError || (() => {});
    this.onStateChange = options.onStateChange || (() => {});

    this._initRecognizer();
  }

  _initRecognizer() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("[InstantSTT] Web Speech API not supported in this browser.");
      return;
    }

    try {
      if (this.recognition) {
        try { this.recognition.abort(); } catch (e) {}
      }

      this.recognition = new SpeechRecognition();
      this.recognition.continuous = this.continuous;
      this.recognition.interimResults = this.interimResults;
      this.recognition.lang = this.lang;
      this.recognition.maxAlternatives = 1;

      this.recognition.onstart = () => {
        this.isListening = true;
        this.onStateChange({ isListening: true });
      };

      this.recognition.onresult = (event) => {
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const res = event.results[i];
          if (res.isFinal) {
            this.accumulatedTranscript += res[0].transcript + ' ';
          } else {
            interim += res[0].transcript;
          }
        }

        this.interimTranscript = interim;
        const currentDisplay = (this.accumulatedTranscript + (interim ? ' ' + interim : '')).trim();
        this.onInterim(currentDisplay, interim, this.accumulatedTranscript.trim());
      };

      this.recognition.onerror = (event) => {
        // 'no-speech' is expected during thinking pauses
        if (event.error !== 'no-speech' && event.error !== 'aborted') {
          console.debug("[InstantSTT] Speech recognition event:", event.error);
          this.onError(event);
        }
      };

      this.recognition.onend = () => {
        this.onStateChange({ isListening: false });
        // Automatically restart if user still has recording toggled ON
        if (this.isListening) {
          try {
            this.recognition.start();
          } catch (e) {
            this.isListening = false;
          }
        }
      };
    } catch (err) {
      console.warn("[InstantSTT] Initialization warning:", err);
    }
  }

  start() {
    // Prevent voice-over overlap: cancel any playing TTS synthesis
    if ('speechSynthesis' in window) {
      try { window.speechSynthesis.cancel(); } catch (e) {}
    }

    if (!this.recognition) {
      this._initRecognizer();
    }
    if (!this.recognition) return;

    this.accumulatedTranscript = '';
    this.interimTranscript = '';
    this.isListening = true;

    try {
      this.recognition.start();
    } catch (e) {
      // If already started or aborting, re-init and start
      this._initRecognizer();
      try { this.recognition.start(); } catch (err) {}
    }
  }

  stop() {
    this.isListening = false;
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }
    const finalClean = (this.accumulatedTranscript + (this.interimTranscript ? ' ' + this.interimTranscript : '')).trim();
    this.onFinal(finalClean);
    return finalClean;
  }

  getTranscript() {
    return (this.accumulatedTranscript + (this.interimTranscript ? ' ' + this.interimTranscript : '')).trim();
  }

  clear() {
    this.accumulatedTranscript = '';
    this.interimTranscript = '';
  }
}

// Attach globally
window.InstantSTTHandler = InstantSTTHandler;

