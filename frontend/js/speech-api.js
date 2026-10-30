/**
 * IMAIRA+ Speech API Client
 * 
 * Provides unified communication with the backend speech services:
 * - Audio transcription with glossary evaluation (/api/speech/transcribe)
 * - Text-to-speech audio synthesis (/api/speech/synthesize)
 * - Provider metadata and health (/api/speech/providers)
 */

class SpeechApiClient {
  constructor(baseUrl = "http://localhost:5000/api/speech") {
    this.baseUrl = baseUrl;
  }

  /**
   * Upload an audio blob for transcription and glossary analysis.
   * 
   * @param {Blob} audioBlob - Recorded audio file (WebM, WAV, etc.)
   * @param {Object} options - { language: "en-IN", questionContext: "", interviewId: "" }
   * @returns {Promise<Object>} Transcription result with correction_candidates
   */
  async transcribeAudio(audioBlob, options = {}) {
    const formData = new FormData();
    const filename = options.filename || "recording.webm";
    formData.append("audio", audioBlob, filename);

    if (options.language) {
      formData.append("language", options.language);
    }
    if (options.questionContext) {
      formData.append("question_context", options.questionContext);
    }
    if (options.interviewId) {
      formData.append("interview_id", options.interviewId);
    }

    const response = await fetch(`${this.baseUrl}/transcribe`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      let errDetails;
      try {
        errDetails = await response.json();
      } catch (e) {
        errDetails = { message: response.statusText };
      }
      throw new Error(errDetails.message || `Transcription failed with HTTP ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Synthesize text to speech audio via the backend.
   * 
   * @param {string} text - Text to synthesize
   * @param {Object} options - { language: "en-IN", voice: "default" }
   * @returns {Promise<Blob>} Audio blob for playback
   */
  async synthesizeSpeech(text, options = {}) {
    const payload = {
      text,
      language: options.language || "en-IN",
      voice: options.voice,
      speaking_rate: options.speakingRate || 1.0
    };

    const response = await fetch(`${this.baseUrl}/synthesize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      let errMsg = `Synthesis failed with HTTP ${response.status}`;
      try {
        const json = await response.json();
        errMsg = json.message || errMsg;
      } catch (e) {
        // Response wasn't JSON
      }
      throw new Error(errMsg);
    }

    return await response.blob();
  }

  /**
   * Fetch active provider information and glossary status.
   */
  async getProviders() {
    try {
      const response = await fetch(`${this.baseUrl}/providers`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      return data.data;
    } catch (err) {
      console.warn("[SpeechApi] Could not fetch provider metadata:", err.message);
      return null;
    }
  }
}

// Global instance attached to window
window.SpeechApiClient = SpeechApiClient;
window.speechApi = new SpeechApiClient();
