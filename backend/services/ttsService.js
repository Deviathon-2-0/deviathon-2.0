/**
 * IMAIRA+ Text-to-Speech Service
 * 
 * Provider-agnostic TTS abstraction layer.
 * Currently uses a mock provider for development.
 * Ready to plug in Google Cloud TTS, Azure TTS, or other providers
 * when API credentials become available.
 */

// Provider configuration
function getActiveProvider() {
  const envVal = process.env.TTS_PROVIDER;
  if (!envVal || envVal === "undefined") return "google-tts";
  return envVal;
}

const PROVIDER_TIMEOUT_MS = parseInt(process.env.TTS_TIMEOUT_MS || "15000", 10);
const MAX_TEXT_LENGTH = 5000;

/**
 * Validate a TTS synthesis request.
 * @param {string} text - Text to synthesize
 * @returns {{ valid: boolean, error?: string }}
 */
function validateSynthesisRequest(text) {
  if (!text || typeof text !== "string") {
    return { valid: false, error: "Text is required for synthesis" };
  }

  const trimmed = text.trim();
  if (trimmed.length === 0) {
    return { valid: false, error: "Text cannot be empty" };
  }

  if (trimmed.length > MAX_TEXT_LENGTH) {
    return {
      valid: false,
      error: `Text length ${trimmed.length} exceeds maximum of ${MAX_TEXT_LENGTH} characters`
    };
  }

  return { valid: true };
}

/**
 * Synthesize speech from text.
 * @param {string} text - Text to synthesize
 * @param {Object} options - { voice, language, speakingRate, requireReal, provider }
 * @returns {Promise<Object>} { audioBuffer, contentType, provider, isMock, isPlaceholder, ... }
 */
async function synthesize(text, options = {}) {
  const { voice, language, speakingRate, requireReal } = options;
  const currentProvider = options.provider || getActiveProvider();

  if (requireReal && currentProvider === "mock") {
    throw new Error(
      "Real speech synthesis provider is not configured. Active provider is 'mock'. Configure GOOGLE_APPLICATION_CREDENTIALS or Azure credentials in .env, or use 'google-tts'."
    );
  }

  switch (currentProvider) {
    case "google-tts":
    case "google-translate":
      return await googleTtsSynthesize(text, options);

    case "mock":
      return await mockSynthesize(text, options);

    case "google":
      return await googleCloudSynthesize(text, options);

    case "azure":
      return await azureSynthesize(text, options);

    default:
      throw new Error(`Unknown TTS provider: ${currentProvider}. Set TTS_PROVIDER to one of: google-tts, mock, google, azure`);
  }
}

/**
 * Split text into chunks bounded by max length without splitting words.
 */
function splitTextIntoChunks(text, maxLen = 180) {
  const clean = text.trim();
  if (clean.length <= maxLen) return [clean];

  const words = clean.split(/\s+/);
  const chunks = [];
  let current = "";

  for (const word of words) {
    if ((current + " " + word).trim().length <= maxLen) {
      current = (current + " " + word).trim();
    } else {
      if (current) chunks.push(current);
      current = word;
    }
  }
  if (current) chunks.push(current);

  return chunks.length > 0 ? chunks : [clean];
}

/**
 * Real Text-to-Speech synthesis using Google's speech service.
 * Requires zero credentials and produces real, high-quality synthesized speech in MP3 format.
 * Supports en-IN (Indian English), en-US, en-GB, and other accents.
 */
async function googleTtsSynthesize(text, options = {}) {
  const language = options.language || "en-IN";
  const langCode = language.includes("IN") ? "en-IN" : language.includes("GB") ? "en-GB" : "en-US";

  // Split text into chunks <= 180 chars to adhere to URL length limits
  const chunks = splitTextIntoChunks(text, 180);
  const audioBuffers = [];

  for (const chunk of chunks) {
    const encoded = encodeURIComponent(chunk);
    const url = `https://translate.google.com/translate_tts?ie=UTF-8&q=${encoded}&tl=${langCode}&client=tw-ob`;

    const response = await Promise.race([
      fetch(url, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
      }),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error("TTS provider timeout")), PROVIDER_TIMEOUT_MS)
      )
    ]);

    if (!response.ok) {
      throw new Error(`Google TTS service responded with HTTP ${response.status}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    audioBuffers.push(Buffer.from(arrayBuffer));
  }

  const combinedBuffer = Buffer.concat(audioBuffers);

  return {
    audioBuffer: combinedBuffer,
    contentType: "audio/mpeg",
    provider: "google-tts",
    isMock: false,
    isPlaceholder: false,
    voice: `google-natural-${langCode}`,
    language: langCode,
    _meta: {
      is_mock: false,
      is_placeholder: false,
      real_speech: true,
      provider: "google-tts",
      chunks: chunks.length,
      bytes: combinedBuffer.length,
      language: langCode
    }
  };
}

/**
 * Official Google Cloud Text-to-Speech (requires service account credentials).
 */
async function googleCloudSynthesize(text, options = {}) {
  const credentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
  if (!credentialsPath) {
    throw new Error("GOOGLE_APPLICATION_CREDENTIALS not configured. Set path to Google service account JSON in .env or switch to 'google-tts'.");
  }

  let tts;
  try {
    tts = require("@google-cloud/text-to-speech");
  } catch (e) {
    throw new Error("Package @google-cloud/text-to-speech is not installed. Run 'npm install @google-cloud/text-to-speech'.");
  }

  const client = new tts.TextToSpeechClient();
  const [response] = await Promise.race([
    client.synthesizeSpeech({
      input: { text },
      voice: {
        languageCode: options.language || "en-IN",
        name: options.voice || "en-IN-Wavenet-A",
        ssmlGender: "NEUTRAL"
      },
      audioConfig: {
        audioEncoding: "MP3",
        speakingRate: options.speakingRate || 1.0,
        pitch: 0
      }
    }),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("TTS provider timeout")), PROVIDER_TIMEOUT_MS)
    )
  ]);

  return {
    audioBuffer: Buffer.from(response.audioContent),
    contentType: "audio/mp3",
    provider: "google",
    isMock: false,
    isPlaceholder: false,
    voice: options.voice || "en-IN-Wavenet-A",
    language: options.language || "en-IN",
    _meta: { real_speech: true, provider: "google" }
  };
}

/**
 * Azure Cognitive Services Speech (requires AZURE_SPEECH_KEY).
 */
async function azureSynthesize(text, options = {}) {
  const key = process.env.AZURE_SPEECH_KEY;
  const region = process.env.AZURE_SPEECH_REGION;
  if (!key || !region) {
    throw new Error("AZURE_SPEECH_KEY or AZURE_SPEECH_REGION not configured in .env.");
  }

  let sdk;
  try {
    sdk = require("microsoft-cognitiveservices-speech-sdk");
  } catch (e) {
    throw new Error("Package microsoft-cognitiveservices-speech-sdk is not installed.");
  }

  const speechConfig = sdk.SpeechConfig.fromSubscription(key, region);
  speechConfig.speechSynthesisVoiceName = options.voice || "en-IN-NeerjaNeural";
  const synthesizer = new sdk.SpeechSynthesizer(speechConfig, null);

  const result = await new Promise((resolve, reject) => {
    synthesizer.speakTextAsync(
      text,
      (res) => {
        if (res.reason === sdk.ResultReason.SynthesizingAudioCompleted) {
          resolve(Buffer.from(res.audioData));
        } else {
          reject(new Error(`Azure synthesis failed: ${res.errorDetails}`));
        }
        synthesizer.close();
      },
      (err) => {
        synthesizer.close();
        reject(err);
      }
    );
  });

  return {
    audioBuffer: result,
    contentType: "audio/wav",
    provider: "azure",
    isMock: false,
    isPlaceholder: false,
    voice: options.voice || "en-IN-NeerjaNeural",
    language: options.language || "en-IN",
    _meta: { real_speech: true, provider: "azure" }
  };
}

/**
 * Mock TTS provider for development.
 * Produces a simulated WAV file with duration proportional to the text length,
 * audible sample data (modulated cadence tone), and explicit placeholder metadata.
 */
async function mockSynthesize(text, options = {}) {
  const delay = 100 + Math.random() * 200;
  await new Promise(resolve => setTimeout(resolve, delay));

  const words = text.trim().split(/\s+/).filter(Boolean);
  const speakingRate = Math.max(0.5, Math.min(2.0, Number(options.speakingRate) || 1.0));
  const durationSec = Math.max(1.2, +(words.length / (2.33 * speakingRate)).toFixed(2));

  const sampleRate = 22050;
  const numSamples = Math.floor(sampleRate * durationSec);
  const dataSize = numSamples * 2; // 16-bit mono
  const headerSize = 44;

  const buffer = Buffer.alloc(headerSize + dataSize);

  // RIFF header
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(headerSize + dataSize - 8, 4);
  buffer.write("WAVE", 8);

  // fmt sub-chunk
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);       // Sub-chunk size
  buffer.writeUInt16LE(1, 20);        // PCM format
  buffer.writeUInt16LE(1, 22);        // Mono
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * 2, 28); // Byte rate
  buffer.writeUInt16LE(2, 32);        // Block align
  buffer.writeUInt16LE(16, 34);       // Bits per sample

  // data sub-chunk
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataSize, 40);

  const toneFreq = 440;
  for (let i = 0; i < numSamples; i++) {
    const t = i / sampleRate;
    const cadence = 0.5 + 0.5 * Math.sin(2 * Math.PI * 3.0 * t);
    const envelope = Math.min(1.0, Math.min(t / 0.05, (durationSec - t) / 0.05));
    const sample = Math.floor(Math.sin(2 * Math.PI * toneFreq * t) * cadence * envelope * 3000);
    buffer.writeInt16LE(sample, headerSize + i * 2);
  }

  return {
    audioBuffer: buffer,
    contentType: "audio/wav",
    provider: "mock",
    isMock: true,
    isPlaceholder: true,
    voice: options.voice || "mock-placeholder",
    language: options.language || "en-IN",
    durationSeconds: durationSec,
    sampleRate,
    numSamples,
    processing_time_ms: Math.round(delay),
    _meta: {
      is_mock: true,
      is_placeholder: true,
      notice: "Mock placeholder audio generated with calculated duration. Real speech synthesis requires configuring a cloud provider in .env.",
      text_length: text.length,
      word_count: words.length,
      duration_seconds: durationSec
    }
  };
}

/**
 * Get information about the currently configured TTS provider.
 */
function getProviderInfo(customProvider) {
  const provider = customProvider || getActiveProvider();
  const isMock = provider === "mock";
  const isReal = !isMock;

  const voicesByProvider = {
    "google-tts": ["google-natural-en-IN", "google-natural-en-US", "google-natural-en-GB"],
    "google": ["en-IN-Wavenet-A", "en-IN-Wavenet-B", "en-IN-Wavenet-C"],
    "azure": ["en-IN-NeerjaNeural", "en-IN-PrabhatNeural"],
    "mock": ["mock-placeholder"]
  };

  const info = {
    provider,
    is_mock: isMock,
    is_placeholder: isMock,
    real_speech: isReal,
    status: isMock ? "mock_placeholder" : "active_real_speech",
    message: isMock
      ? "Mock TTS provider active: produces simulated placeholder audio with calculated duration. Set TTS_PROVIDER=google-tts for real speech without credentials, or configure cloud credentials."
      : `Real TTS provider active (${provider}). Produces natural synthesized speech.`,
    max_text_length: MAX_TEXT_LENGTH,
    timeout_ms: PROVIDER_TIMEOUT_MS,
    available_voices: voicesByProvider[provider] || [provider],
    supported_languages: ["en-US", "en-IN", "en-GB"]
  };

  return info;
}

module.exports = {
  validateSynthesisRequest,
  synthesize,
  getProviderInfo,
  splitTextIntoChunks,
  MAX_TEXT_LENGTH
};
