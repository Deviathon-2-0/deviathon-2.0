/**
 * IMAIRA+ Speech-to-Text Service
 * 
 * Provider-agnostic STT abstraction layer.
 * Currently uses a mock provider for development.
 * Ready to plug in Sarvam AI, Deepgram, or Google Cloud Speech-to-Text
 * when API credentials become available.
 * 
 * IMPORTANT: This service preserves the original transcript exactly as returned
 * by the provider. It does NOT silently correct or rewrite transcriptions.
 */
const fs = require("fs");
const path = require("path");

// Provider configuration — set STT_PROVIDER in .env
const STT_PROVIDER = process.env.STT_PROVIDER || "mock";

// Supported audio MIME types and their file extensions
const SUPPORTED_AUDIO_TYPES = {
  "audio/webm": [".webm"],
  "audio/wav": [".wav"],
  "audio/wave": [".wav"],
  "audio/x-wav": [".wav"],
  "audio/mp3": [".mp3"],
  "audio/mpeg": [".mp3"],
  "audio/ogg": [".ogg"],
  "audio/mp4": [".m4a"],
  "audio/x-m4a": [".m4a"],
  "audio/m4a": [".m4a"]
};

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25 MB
const PROVIDER_TIMEOUT_MS = parseInt(process.env.STT_TIMEOUT_MS || "30000", 10);

/**
 * Validate an uploaded audio file before transcription.
 * @param {Object} file - Multer file object
 * @returns {{ valid: boolean, error?: string }}
 */
function validateAudioFile(file) {
  if (!file) {
    return { valid: false, error: "No audio file provided" };
  }

  if (file.size === 0) {
    return { valid: false, error: "Audio file is empty (0 bytes)" };
  }

  if (file.size > MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `File size ${(file.size / 1024 / 1024).toFixed(1)}MB exceeds maximum of ${MAX_FILE_SIZE / 1024 / 1024}MB`
    };
  }

  // Check MIME type
  const mimeType = (file.mimetype || "").toLowerCase();
  if (!SUPPORTED_AUDIO_TYPES[mimeType]) {
    return {
      valid: false,
      error: `Unsupported audio format: ${mimeType}. Supported: ${Object.keys(SUPPORTED_AUDIO_TYPES).join(", ")}`
    };
  }

  return { valid: true };
}

/**
 * Transcribe audio using the configured provider.
 * @param {string} filePath - Absolute path to the audio file
 * @param {Object} options - { language, interviewId, mimeType }
 * @returns {Promise<Object>} Transcription result
 */
async function transcribe(filePath, options = {}) {
  const { language, interviewId, mimeType } = options;

  switch (STT_PROVIDER) {
    case "mock":
      return await mockTranscribe(filePath, options);

    // ── Ready for real providers ──
    // case "deepgram":
    //   return await deepgramTranscribe(filePath, options);
    // case "sarvam":
    //   return await sarvamTranscribe(filePath, options);
    // case "google":
    //   return await googleTranscribe(filePath, options);

    default:
      throw new Error(`Unknown STT provider: ${STT_PROVIDER}. Set STT_PROVIDER to one of: mock, deepgram, sarvam, google`);
  }
}

/**
 * Mock provider for development and testing.
 * Returns a simulated transcription response.
 */
async function mockTranscribe(filePath, options = {}) {
  // Simulate processing delay (200-800ms)
  const delay = 200 + Math.random() * 600;
  await new Promise(resolve => setTimeout(resolve, delay));

  // Verify the file exists and is readable
  if (!fs.existsSync(filePath)) {
    throw new Error("Audio file not found for transcription");
  }

  const fileSize = fs.statSync(filePath).size;
  // Rough duration estimate: ~16KB per second at typical web audio bitrate
  const estimatedDurationSec = Math.max(1, Math.round(fileSize / 16000));

  return {
    status: "completed",
    transcript: "[Mock transcription] This is a simulated transcription for development. Connect a real STT provider (Deepgram, Sarvam AI, or Google Cloud Speech) by setting STT_PROVIDER and the corresponding API key in .env.",
    segments: [
      {
        start_seconds: 0.0,
        end_seconds: estimatedDurationSec,
        text: "[Mock transcription] This is a simulated transcription for development."
      }
    ],
    provider: "mock",
    processing_time_ms: Math.round(delay),
    _meta: {
      note: "Mock provider — no real transcription was performed",
      file_size_bytes: fileSize,
      estimated_duration_seconds: estimatedDurationSec
    }
  };
}

// ══════════════════════════════════════════════════════════════════════════
// PROVIDER STUBS — uncomment and configure when credentials are available
// ══════════════════════════════════════════════════════════════════════════

/*
async function deepgramTranscribe(filePath, options = {}) {
  // Requires: npm install @deepgram/sdk
  // Env: DEEPGRAM_API_KEY
  const { Deepgram } = require("@deepgram/sdk");
  const apiKey = process.env.DEEPGRAM_API_KEY;
  if (!apiKey) throw new Error("DEEPGRAM_API_KEY not configured");

  const deepgram = new Deepgram(apiKey);
  const audioBuffer = fs.readFileSync(filePath);
  const mimeType = options.mimeType || "audio/webm";

  const response = await Promise.race([
    deepgram.transcription.preRecorded(
      { buffer: audioBuffer, mimetype: mimeType },
      {
        model: "nova-2",
        language: options.language || "en-IN",
        smart_format: true,
        utterances: true,
        punctuate: true,
      }
    ),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("STT provider timeout")), PROVIDER_TIMEOUT_MS)
    )
  ]);

  const result = response.results?.channels?.[0]?.alternatives?.[0];
  if (!result) throw new Error("No transcription result from Deepgram");

  return {
    status: "completed",
    transcript: result.transcript || "",
    segments: (result.words || []).map(w => ({
      start_seconds: w.start,
      end_seconds: w.end,
      text: w.punctuated_word || w.word,
      confidence: w.confidence
    })),
    provider: "deepgram",
    processing_time_ms: null,
  };
}
*/

/*
async function sarvamTranscribe(filePath, options = {}) {
  // Sarvam AI — Indian English specialist
  // Env: SARVAM_API_KEY
  const apiKey = process.env.SARVAM_API_KEY;
  if (!apiKey) throw new Error("SARVAM_API_KEY not configured");

  const FormData = require("form-data");
  const fetch = require("node-fetch");

  const form = new FormData();
  form.append("file", fs.createReadStream(filePath));
  form.append("language_code", options.language || "en-IN");

  const response = await Promise.race([
    fetch("https://api.sarvam.ai/speech-to-text", {
      method: "POST",
      headers: {
        "api-subscription-key": apiKey,
        ...form.getHeaders()
      },
      body: form
    }),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("STT provider timeout")), PROVIDER_TIMEOUT_MS)
    )
  ]);

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Sarvam API error ${response.status}: ${err}`);
  }

  const data = await response.json();

  return {
    status: "completed",
    transcript: data.transcript || "",
    segments: [], // Sarvam may not provide word-level timestamps
    provider: "sarvam",
    processing_time_ms: null,
  };
}
*/

/**
 * Get information about the currently configured STT provider.
 */
function getProviderInfo() {
  return {
    provider: STT_PROVIDER,
    supported_formats: Object.keys(SUPPORTED_AUDIO_TYPES),
    max_file_size_mb: MAX_FILE_SIZE / 1024 / 1024,
    timeout_ms: PROVIDER_TIMEOUT_MS,
    is_mock: STT_PROVIDER === "mock"
  };
}

module.exports = {
  validateAudioFile,
  transcribe,
  getProviderInfo,
  SUPPORTED_AUDIO_TYPES,
  MAX_FILE_SIZE
};
