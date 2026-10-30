/**
 * IMAIRA+ Speech Recorder (STT)
 * 
 * High-performance speech input engine combining:
 * 1. Live browser SpeechRecognition (Web Speech API) with per-session re-instantiation.
 * 2. Question-index tracking to guarantee answers are never bound to mutated globals.
 * 3. Interim-to-final transcript promotion preventing lost speech on quick stops.
 * 4. MediaRecorder stream capture for backend glossary analysis & accent evaluation.
 */

class SpeechRecorder {
  constructor(options = {}) {
    this.api = options.api || window.speechApi;
    this.language = options.language || "en-IN";
    this.mediaStream = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.recognition = null;
    this.startTime = null;
    this.timerInterval = null;
    this.activeQuestionIndex = null;

    // Transcript accumulation
    this.finalTranscript = "";
    this.interimTranscript = "";

    // Callbacks
    this.onInterimResult = options.onInterimResult || (() => {});
    this.onFinalResult = options.onFinalResult || (() => {});
    this.onCandidates = options.onCandidates || (() => {});
    this.onStateChange = options.onStateChange || (() => {});
    this.onError = options.onError || (() => {});
    this.onTimerTick = options.onTimerTick || (() => {});

    // Check SpeechRecognition support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.hasSpeechRecognition = !!SpeechRecognition;
    this._initRecognition();
  }

  /**
   * Initialize or re-instantiate SpeechRecognition instance.
   * Browsers (especially Chrome/WebKit) require a clean instance after stops
   * to avoid 'recognition already started' or silent dropouts on subsequent runs.
   */
  _initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    if (this.recognition) {
      try {
        this.recognition.onresult = null;
        this.recognition.onerror = null;
        this.recognition.onend = null;
        this.recognition.abort();
      } catch (e) {}
      this.recognition = null;
    }

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = this.language;
      this.recognition.maxAlternatives = 1;

      this.recognition.onresult = (event) => this._handleRecognitionResult(event);
      this.recognition.onerror = (event) => {
        const errType = event.error;
        console.warn("[SpeechRecorder] Speech recognition event error:", errType);
        if (errType === "not-allowed") {
          this.onError(new Error("Microphone permission denied"), this.activeQuestionIndex);
        } else if (errType !== "no-speech" && errType !== "aborted") {
          this.onError(new Error(`Speech recognition error: ${errType}`), this.activeQuestionIndex);
        }
      };

      this.recognition.onend = () => {
        // Auto-restart if we are still marked as recording (browser recognition can time out during silence)
        if (this.isRecording && this.recognition) {
          try {
            this.recognition.start();
          } catch (e) {
            // Ignore benign restart collisions
          }
        }
      };
    } catch (err) {
      console.warn("[SpeechRecorder] Could not initialize SpeechRecognition engine:", err);
    }
  }

  /**
   * Handle Web Speech Recognition live events.
   */
  _handleRecognitionResult(event) {
    let interim = "";
    const qIdx = this.activeQuestionIndex;

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      const item = event.results[i];
      const text = item[0] ? item[0].transcript : "";
      if (item.isFinal) {
        const trimmed = text.trim();
        if (trimmed) {
          this.finalTranscript += (this.finalTranscript ? " " : "") + trimmed;
          this.onFinalResult(this.finalTranscript, qIdx);
        }
      } else {
        interim += text;
      }
    }

    this.interimTranscript = interim;
    this.onInterimResult({
      final: this.finalTranscript,
      interim: this.interimTranscript,
      questionIndex: qIdx
    });
  }

  /**
   * Start recording audio and live speech recognition.
   * Accepts { questionIndex } so speech is strictly associated with the target question.
   */
  async start(options = {}) {
    if (this.isRecording) return;

    try {
      this.activeQuestionIndex = options.questionIndex !== undefined ? options.questionIndex : null;
      this.finalTranscript = "";
      this.interimTranscript = "";
      this.audioChunks = [];

      // Always re-initialize SpeechRecognition to avoid stale Chrome state
      this._initRecognition();

      // Request microphone access
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      // Setup MediaRecorder
      const mimeType = this._getSupportedMimeType();
      this.mediaRecorder = new MediaRecorder(this.mediaStream, mimeType ? { mimeType } : {});

      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          this.audioChunks.push(e.data);
        }
      };

      this.mediaRecorder.start(250);
      this.isRecording = true;

      // Start live speech recognition if available
      if (this.recognition) {
        try {
          this.recognition.lang = this.language;
          this.recognition.start();
        } catch (e) {
          console.warn("[SpeechRecorder] Speech recognition start warning:", e);
        }
      }

      // Start timer
      this.startTime = Date.now();
      clearInterval(this.timerInterval);
      this.timerInterval = setInterval(() => {
        if (!this.isRecording) return;
        const elapsedSec = Math.floor((Date.now() - this.startTime) / 1000);
        this.onTimerTick(elapsedSec);
      }, 1000);

      this.onStateChange({ isRecording: true, questionIndex: this.activeQuestionIndex });
      console.log(`[SpeechRecorder] Audio recording started for Question index ${this.activeQuestionIndex}`);
    } catch (err) {
      console.error("[SpeechRecorder] Failed to start recording:", err);
      this.isRecording = false;
      this.onError(err, this.activeQuestionIndex);
      throw err;
    }
  }

  /**
   * Stop recording and process transcript / glossary candidates.
   * Waits for speech recognition and pending transcription work to settle.
   * 
   * @param {Object} options - { questionContext: string, questionIndex: number }
   * @returns {Promise<Object>} Processed result with transcript, candidates, and questionIndex
   */
  async stop(options = {}) {
    const targetQIndex = options.questionIndex !== undefined ? options.questionIndex : this.activeQuestionIndex;

    if (!this.isRecording) {
      const existing = (this.finalTranscript || this.interimTranscript || "").trim();
      return { transcript: existing, candidates: [], questionIndex: targetQIndex };
    }

    this.isRecording = false;
    clearInterval(this.timerInterval);

    // Stop Web Speech recognition
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }

    // Grace period for browser speech engine to deliver pending final speech packets
    await new Promise((resolve) => setTimeout(resolve, 200));

    // Reliable speech finalization: if finalTranscript is empty, promote interimTranscript
    if (!this.finalTranscript.trim() && this.interimTranscript.trim()) {
      this.finalTranscript = this.interimTranscript.trim();
      this.onFinalResult(this.finalTranscript, targetQIndex);
    }

    // Stop MediaRecorder and assemble Blob with safety timeout
    const audioBlob = await new Promise((resolve) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === "inactive") {
        resolve(null);
        return;
      }

      let resolved = false;
      const finish = () => {
        if (resolved) return;
        resolved = true;
        const mimeType = (this.mediaRecorder && this.mediaRecorder.mimeType) || "audio/webm";
        const blob = new Blob(this.audioChunks, { type: mimeType });
        resolve(blob);
      };

      this.mediaRecorder.onstop = finish;
      try {
        this.mediaRecorder.stop();
      } catch (e) {
        finish();
      }
      setTimeout(finish, 600); // Safety fallback
    });

    // Release microphone tracks
    if (this.mediaStream) {
      try {
        this.mediaStream.getTracks().forEach((track) => track.stop());
      } catch (e) {}
      this.mediaStream = null;
    }

    this.onStateChange({ isRecording: false, isProcessing: true, questionIndex: targetQIndex });

    let finalResult = {
      transcript: this.finalTranscript.trim(),
      candidates: [],
      questionIndex: targetQIndex
    };

    // If we have audio data, send to backend for glossary analysis & genuine server transcription
    if (audioBlob && audioBlob.size > 0 && this.api) {
      try {
        console.log(`[SpeechRecorder] Sending ${(audioBlob.size / 1024).toFixed(1)}KB audio to backend for Question ${targetQIndex}...`);
        const serverResult = await this.api.transcribeAudio(audioBlob, {
          language: this.language,
          questionContext: options.questionContext || ""
        });

        const candidates = serverResult.correction_candidates || [];
        this.onCandidates(candidates, targetQIndex);

        // If client Web Speech produced nothing, check if server produced a GENUINE transcript (not mock)
        if (!finalResult.transcript && serverResult.transcript) {
          const isMockTranscript = typeof serverResult.transcript === "string" && (
            serverResult.transcript.startsWith("[Mock transcription]") ||
            serverResult.provider === "mock"
          );
          if (!isMockTranscript) {
            finalResult.transcript = serverResult.transcript.trim();
            this.finalTranscript = finalResult.transcript;
            this.onFinalResult(finalResult.transcript, targetQIndex);
          } else {
            console.log("[SpeechRecorder] Ignored mock server transcription to preserve candidate answer integrity.");
          }
        }

        finalResult.candidates = candidates;
        finalResult.serverMeta = serverResult._meta;
      } catch (err) {
        console.warn("[SpeechRecorder] Server transcription fallback / glossary check:", err.message);
      }
    }

    this.onStateChange({ isRecording: false, isProcessing: false, questionIndex: targetQIndex });
    return finalResult;
  }

  /**
   * Reset the current transcript buffers.
   */
  clearTranscript() {
    this.finalTranscript = "";
    this.interimTranscript = "";
    this.onInterimResult({ final: "", interim: "", questionIndex: this.activeQuestionIndex });
  }

  /**
   * Full session reset for retakes or new interview sessions.
   * Completely cleans up audio tracks, recorder buffers, and SpeechRecognition state.
   */
  reset() {
    this.isRecording = false;
    clearInterval(this.timerInterval);
    if (this.mediaStream) {
      try {
        this.mediaStream.getTracks().forEach((track) => track.stop());
      } catch (e) {}
      this.mediaStream = null;
    }
    if (this.mediaRecorder && this.mediaRecorder.state !== "inactive") {
      try {
        this.mediaRecorder.stop();
      } catch (e) {}
    }
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.finalTranscript = "";
    this.interimTranscript = "";
    this.activeQuestionIndex = null;
    this._initRecognition();
    this.onStateChange({ isRecording: false, isProcessing: false, questionIndex: null });
  }

  /**
   * Set target speech recognition language (e.g. "en-IN", "en-US").
   */
  setLanguage(lang) {
    this.language = lang;
    if (this.recognition) {
      this.recognition.lang = lang;
    }
  }

  /**
   * Detect supported audio MIME type in the current browser.
   */
  _getSupportedMimeType() {
    const types = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/mp4",
      "audio/wav"
    ];
    for (const type of types) {
      if (MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }
    return "";
  }
}

// Global instance attached to window
window.SpeechRecorder = SpeechRecorder;
window.speechRecorder = new SpeechRecorder();
