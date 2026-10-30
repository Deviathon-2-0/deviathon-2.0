/**
 * IMAIRA+ Speech Controller
 * 
 * Handles STT transcription and TTS synthesis requests.
 * Orchestrates file validation, provider calls, glossary matching,
 * and temporary file cleanup.
 */
const sttService = require("../services/sttService");
const ttsService = require("../services/ttsService");
const glossaryService = require("../services/glossaryService");
const { cleanupTempFile } = require("../middleware/upload");

/**
 * POST /api/speech/transcribe
 * 
 * Accepts multipart/form-data with:
 *   - audio: audio file (required)
 *   - language: language hint, e.g. "en-IN" (optional)
 *   - interview_id: session identifier (optional)
 */
exports.transcribe = async (req, res) => {
  const startTime = Date.now();
  let tempFilePath = null;

  try {
    const file = req.file;

    // Validate the uploaded file
    const validation = sttService.validateAudioFile(file);
    if (!validation.valid) {
      // Clean up if multer saved a partial file
      if (file && file.path) cleanupTempFile(file.path);
      return res.status(400).json({
        error: "Invalid audio file",
        message: validation.error
      });
    }

    tempFilePath = file.path;
    const language = req.body.language || "en-IN";
    const interviewId = req.body.interview_id || null;

    console.log(`[Speech] Transcription request: ${(file.size / 1024).toFixed(1)}KB, ${file.mimetype}, lang=${language}`);

    // Call STT provider
    const result = await sttService.transcribe(tempFilePath, {
      language,
      interviewId,
      mimeType: file.mimetype
    });

    // Run glossary correction candidates (if transcript is non-empty)
    let correctionCandidates = [];
    if (result.transcript && result.transcript.length > 0) {
      // Use the current question as context if provided
      const questionContext = req.body.question_context || "";
      correctionCandidates = glossaryService.generateCorrectionCandidates(
        result.transcript,
        questionContext
      );
    }

    const totalTimeMs = Date.now() - startTime;

    // Build response
    const response = {
      status: "completed",
      transcript: result.transcript,
      segments: result.segments || [],
      correction_candidates: correctionCandidates,
      provider: result.provider,
      processing_time_ms: totalTimeMs,
      _meta: {
        file_size_bytes: file.size,
        mime_type: file.mimetype,
        language_hint: language,
        interview_id: interviewId,
        glossary: glossaryService.getGlossaryInfo()
      }
    };

    // Clean up temp file after successful transcription
    cleanupTempFile(tempFilePath);
    tempFilePath = null;

    return res.status(200).json(response);
  } catch (err) {
    // Clean up temp file on error
    cleanupTempFile(tempFilePath);

    console.error("[Speech] Transcription error:", err.message);

    // Distinguish provider timeouts from other errors
    if (err.message.includes("timeout")) {
      return res.status(504).json({
        error: "Provider Timeout",
        message: "The transcription provider did not respond in time. Please try again.",
        provider: sttService.getProviderInfo().provider
      });
    }

    if (err.message.includes("not configured") || err.message.includes("API_KEY")) {
      return res.status(503).json({
        error: "Provider Not Configured",
        message: "The STT provider credentials are not configured. Please contact the administrator.",
        provider: sttService.getProviderInfo().provider
      });
    }

    return res.status(500).json({
      error: "Transcription Failed",
      message: err.message || "An unexpected error occurred during transcription"
    });
  }
};

/**
 * POST /api/speech/synthesize
 * 
 * Accepts JSON with:
 *   - text: text to synthesize (required)
 *   - voice: provider voice ID (optional)
 *   - language: e.g. "en-IN" (optional, default "en-IN")
 *   - speaking_rate: float (optional)
 */
exports.synthesize = async (req, res) => {
  try {
    const { text, voice, language, speaking_rate, require_real } = req.body || {};
    const requireReal = require_real === true || 
      req.query?.require_real === "true" || 
      req.headers["x-require-real-tts"] === "true";

    // Validate request
    const validation = ttsService.validateSynthesisRequest(text);
    if (!validation.valid) {
      return res.status(400).json({
        error: "Invalid synthesis request",
        message: validation.error
      });
    }

    console.log(`[Speech] Synthesis request: ${text.length} chars, lang=${language || "en-IN"}, requireReal=${requireReal}`);

    // Call TTS provider
    const result = await ttsService.synthesize(text.trim(), {
      voice: voice || undefined,
      language: language || "en-IN",
      speakingRate: speaking_rate || 1.0,
      requireReal
    });

    // Return audio directly as binary response
    const headers = {
      "Content-Type": result.contentType,
      "Content-Length": result.audioBuffer.length,
      "X-TTS-Provider": result.provider,
      "X-TTS-Is-Mock": result.isMock ? "true" : "false",
      "X-TTS-Is-Placeholder": result.isPlaceholder ? "true" : "false",
      "X-TTS-Real-Speech": result.isPlaceholder ? "false" : "true",
      "X-TTS-Voice": result.voice || "default",
      "Cache-Control": result.isPlaceholder ? "no-cache" : "private, max-age=3600"
    };

    if (result.durationSeconds) {
      headers["X-TTS-Duration-Seconds"] = String(result.durationSeconds);
    }

    if (result.isPlaceholder) {
      headers["X-TTS-Warning"] = "Mock provider generated placeholder audio. Real speech synthesis requires configuring a cloud provider in .env.";
    }

    res.set(headers);
    return res.send(result.audioBuffer);
  } catch (err) {
    console.error("[Speech] Synthesis error:", err.message);

    if (err.message.includes("timeout")) {
      return res.status(504).json({
        error: "Provider Timeout",
        message: "The TTS provider did not respond in time. Please try again."
      });
    }

    if (err.message.includes("not configured") || err.message.includes("API_KEY")) {
      return res.status(503).json({
        error: "Provider Not Configured",
        message: err.message || "The TTS provider credentials are not configured.",
        provider: ttsService.getProviderInfo().provider,
        is_mock: ttsService.getProviderInfo().is_mock
      });
    }

    return res.status(500).json({
      error: "Synthesis Failed",
      message: err.message || "An unexpected error occurred during synthesis"
    });
  }
};

/**
 * GET /api/speech/providers
 * 
 * Returns information about the configured speech providers.
 */
exports.getProviders = (req, res) => {
  res.status(200).json({
    success: true,
    data: {
      stt: sttService.getProviderInfo(),
      tts: ttsService.getProviderInfo(),
      glossary: glossaryService.getGlossaryInfo()
    }
  });
};
