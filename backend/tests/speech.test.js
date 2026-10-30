/**
 * IMAIRA+ Speech Services & Glossary Unit Tests
 * 
 * Uses Node.js native test runner (node --test) and assertions.
 */
require("dotenv").config();
const { describe, it } = require("node:test");
const assert = require("node:assert");
const fs = require("fs");
const path = require("path");

const glossaryService = require("../services/glossaryService");
const sttService = require("../services/sttService");
const ttsService = require("../services/ttsService");
const { validateAudioFile } = require("../services/sttService");
const { cleanupTempFile, ALLOWED_MIME_TYPES, MAX_FILE_SIZE } = require("../middleware/upload");

describe("Glossary Service Tests", () => {
  it("should initialize and load the test glossary fixture", () => {
    const info = glossaryService.getGlossaryInfo();
    assert.strictEqual(info.loaded, true);
    assert.strictEqual(info.isTestFixture, true);
    assert.ok(info.termCount > 0, "Glossary should contain terms");
  });

  it("should match canonical terms directly", () => {
    const match = glossaryService.findCanonicalTerm("kubernetes");
    assert.ok(match, "Should find kubernetes");
    assert.strictEqual(match.canonical, "Kubernetes");
  });

  it("should match common accent/ASR phonetic variants", () => {
    // "coobernetties" / "kubernets" / "koobernetes"
    const match = glossaryService.findCanonicalTerm("koobernetes");
    assert.ok(match, "Should match phonetic variant of Kubernetes");
    assert.strictEqual(match.canonical, "Kubernetes");
  });

  it("should generate correction candidates with confidence scores and context boosts", () => {
    const transcript = "I used koobernetes and postgress for microservice deployment";
    const candidates = glossaryService.generateCorrectionCandidates(
      transcript,
      "Explain your experience with container orchestration in Kubernetes."
    );

    assert.ok(Array.isArray(candidates), "Candidates must be an array");
    assert.ok(candidates.length > 0, "Should generate at least one candidate");

    const k8sCandidate = candidates.find(c => c.suggested === "Kubernetes");
    assert.ok(k8sCandidate, "Should have a candidate for Kubernetes");
    assert.strictEqual(k8sCandidate.original, "koobernetes");
    assert.strictEqual(k8sCandidate.confidence, "high");
  });

  it("should not falsely replace terms when already canonical", () => {
    const transcript = "We deployed on Kubernetes and PostgreSQL";
    const candidates = glossaryService.generateCorrectionCandidates(transcript, "");
    // Already accurate, so no corrections needed for Kubernetes
    const k8s = candidates.find(c => c.original && c.original.toLowerCase() === "kubernetes");
    assert.strictEqual(k8s, undefined);
  });
});

describe("STT Service Tests", () => {
  it("should validate valid audio files correctly", () => {
    const validFile = {
      size: 1024 * 50, // 50KB
      mimetype: "audio/webm",
      path: "/fake/path/audio.webm"
    };
    const result = sttService.validateAudioFile(validFile);
    assert.strictEqual(result.valid, true);
  });

  it("should reject missing or empty audio files", () => {
    const emptyFile = { size: 0, mimetype: "audio/webm" };
    const resEmpty = sttService.validateAudioFile(emptyFile);
    assert.strictEqual(resEmpty.valid, false);

    const resNull = sttService.validateAudioFile(null);
    assert.strictEqual(resNull.valid, false);
  });

  it("should reject oversized files (>25MB)", () => {
    const hugeFile = {
      size: 26 * 1024 * 1024,
      mimetype: "audio/wav"
    };
    const res = sttService.validateAudioFile(hugeFile);
    assert.strictEqual(res.valid, false);
    assert.match(res.error, /exceeds.*25MB/);
  });

  it("should reject unsupported MIME types", () => {
    const invalidFile = {
      size: 5000,
      mimetype: "application/pdf"
    };
    const res = sttService.validateAudioFile(invalidFile);
    assert.strictEqual(res.valid, false);
    assert.match(res.error, /Unsupported audio format/);
  });

  it("should produce valid mock transcript in mock mode", async () => {
    const mockAudioPath = path.join(__dirname, "test_sample.tmp");
    fs.writeFileSync(mockAudioPath, "fake-audio-bytes");

    try {
      const result = await sttService.transcribe(mockAudioPath, {
        language: "en-IN",
        interviewId: "test-session-123"
      });

      assert.strictEqual(result.provider, "mock");
      assert.ok(typeof result.transcript === "string");
      assert.ok(result.transcript.length > 0);
      assert.ok(Array.isArray(result.segments));
    } finally {
      cleanupTempFile(mockAudioPath);
    }
  });
});

describe("TTS Service Tests", () => {
  it("should validate synthesis input text", () => {
    assert.strictEqual(ttsService.validateSynthesisRequest("").valid, false);
    assert.strictEqual(ttsService.validateSynthesisRequest("   ").valid, false);
    assert.strictEqual(ttsService.validateSynthesisRequest("a".repeat(5001)).valid, false);
    assert.strictEqual(ttsService.validateSynthesisRequest("Tell me about yourself.").valid, true);
  });

  it("should report provider status as active real speech", () => {
    const info = ttsService.getProviderInfo();
    assert.strictEqual(info.provider, "google-tts");
    assert.strictEqual(info.is_mock, false);
    assert.strictEqual(info.is_placeholder, false);
    assert.strictEqual(info.real_speech, true);
    assert.strictEqual(info.status, "active_real_speech");
    assert.ok(info.available_voices.some(v => v.includes("en-IN")));
  });

  it("should dynamically select the configured provider when environment changes", () => {
    const original = process.env.TTS_PROVIDER;
    try {
      process.env.TTS_PROVIDER = "mock";
      const mockInfo = ttsService.getProviderInfo();
      assert.strictEqual(mockInfo.provider, "mock");
      assert.strictEqual(mockInfo.is_mock, true);
      assert.strictEqual(mockInfo.is_placeholder, true);
      assert.strictEqual(mockInfo.status, "mock_placeholder");

      process.env.TTS_PROVIDER = "google-tts";
      const realInfo = ttsService.getProviderInfo();
      assert.strictEqual(realInfo.provider, "google-tts");
      assert.strictEqual(realInfo.is_mock, false);
      assert.strictEqual(realInfo.real_speech, true);
      assert.strictEqual(realInfo.status, "active_real_speech");
    } finally {
      if (original) {
        process.env.TTS_PROVIDER = original;
      } else {
        delete process.env.TTS_PROVIDER;
      }
    }
  });

  it("should synthesize real speech into a playable MP3 audio buffer", async () => {
    const text = "Explain the difference between a process and a thread.";
    const result = await ttsService.synthesize(text, { language: "en-IN" });

    assert.strictEqual(result.provider, "google-tts");
    assert.strictEqual(result.isMock, false);
    assert.strictEqual(result.isPlaceholder, false);
    assert.strictEqual(result.contentType, "audio/mpeg");
    assert.ok(Buffer.isBuffer(result.audioBuffer));

    // Verify it returned real MP3 audio data (> 10KB of audio stream)
    assert.ok(
      result.audioBuffer.length > 10000,
      `Real speech MP3 buffer should be substantial (got ${result.audioBuffer.length} bytes)`
    );
  });

  it("should correctly chunk long interview questions without splitting words", () => {
    const longQuestion = "Tell me about a distributed system where you handled data replication under network partitions. How did you maintain consistency, avoid split-brain scenarios, and ensure deterministic leader re-election?";
    const chunks = ttsService.splitTextIntoChunks(longQuestion, 120);

    assert.ok(Array.isArray(chunks));
    assert.ok(chunks.length >= 2, "Long question should be split into multiple chunks");
    for (const chunk of chunks) {
      assert.ok(chunk.length <= 120, `Chunk length ${chunk.length} must be <= 120`);
    }
  });

  it("should handle missing credentials gracefully when official cloud providers are selected", async () => {
    const prevEnv = process.env.GOOGLE_APPLICATION_CREDENTIALS;
    delete process.env.GOOGLE_APPLICATION_CREDENTIALS;

    try {
      await assert.rejects(
        async () => {
          await ttsService.synthesize("Test", { provider: "google" });
        },
        /GOOGLE_APPLICATION_CREDENTIALS not configured/
      );
    } finally {
      if (prevEnv) process.env.GOOGLE_APPLICATION_CREDENTIALS = prevEnv;
    }
  });
});

describe("Upload Middleware & Cleanup", () => {
  it("should safely handle cleanup of non-existent files without throwing", () => {
    assert.doesNotThrow(() => {
      cleanupTempFile(null);
      cleanupTempFile(undefined);
      cleanupTempFile("/tmp/definitely_not_existing_file_12345.tmp");
    });
  });

  it("should define valid allowed MIME types including webm and wav", () => {
    assert.ok(ALLOWED_MIME_TYPES.includes("audio/webm"));
    assert.ok(ALLOWED_MIME_TYPES.includes("audio/wav"));
    assert.strictEqual(MAX_FILE_SIZE, 25 * 1024 * 1024);
  });
});
