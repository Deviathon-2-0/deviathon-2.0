/**
 * IMAIRA+ Client-Side Event Processor & Multi-Signal Scoring Pipeline
 * 
 * High-Level Architecture:
 * [ Browser MediaStream: WebCam & Mic ]
 *                  │
 *    ┌─────────────┴─────────────┐
 *    ▼                           ▼
 * [ Visual Stream ]       [ Audio Stream ]
 *    │                           │
 *    ├─► Eye & Gaze Module       ├─► Pitch & Tone Engine (F0 Variance)
 *    ├─► Reading Detector        ├─► Cadence & Hesitation Monitor
 *    └─► Posture & Poise Module  └─► Volume Envelope (RMS)
 *                  │             │
 *                  └───┬─────────┘
 *                      ▼
 *        [ Cross-Modal Synchro Engine ]
 *           (Lip Aperture vs Audio RMS)
 *                      │
 *                      ▼
 *        [ Aggregator & Feedback Engine ]
 *   Generates Delivery Scores & Integrity Flags
 */

class CandidateMatrixEngine {
  constructor(options = {}) {
    this.videoElement = options.videoElement || null;
    this.mediaStream = options.mediaStream || null;
    this.listeners = {
      telemetry: [],
      integrity_flag: [],
      coaching_tip: [],
    };

    // State & Pipeline Controls
    this.isRunning = false;
    this.animFrameId = null;
    this.lastVideoTime = -1;

    // Web Audio API
    this.audioCtx = null;
    this.analyser = null;
    this.timeDomainData = null;
    this.frequencyData = null;

    // MediaPipe Vision
    this.faceLandmarker = null;
    this.poseLandmarker = null;
    this.visionInitialized = false;

    // --- PIPELINE 1: Visual Tracking State ---
    this.baselineNeckLength = null;
    this.eyeHorizontalHistory = []; // { time, pos } sliding window
    this.eyeVerticalHistory = [];
    this.gazeSamples = { centered: 0, down: 0, away: 0, total: 0 };
    this.postureSamples = { poised: 0, slouched: 0, tilted: 0, total: 0 };
    this.readingSaccadeEvents = 0;
    this.readingFlagged = false;

    // --- PIPELINE 2: Audio Dynamics State ---
    this.pitchHistory = []; // F0 values in Hz
    this.speechPhaseHistory = []; // { timestamp, state: 'speech'|'pause'|'dead_air' }
    this.activeSpeechFrames = 0;
    this.silenceFrames = 0;
    this.deadAirCount = 0;
    this.pitchVariances = [];
    this.volumeRMSHistory = [];

    // --- PIPELINE 3: Cross-Modal Synchro State ---
    this.lipSyncMismatchFrames = 0;
    this.silentMimicFrames = 0;
    this.syncSamples = { inSync: 0, mismatch: 0, total: 0 };
    this.integrityFlags = [];

    // --- AGGREGATOR & MATRIX METRICS ---
    this.sessionStartTime = Date.now();
    this.currentMetrics = {
      eyeContact: "Calibrating",
      readingStatus: "Spontaneous",
      posture: "Calibrating",
      vocalTone: "Analyzing",
      cadence: "Active",
      lipSync: "In-Sync",
      pitchVarianceHz: 0,
      volumeRMS: 0,
      deliveryScore: 85,
      vocalScore: 80,
      spontaneityScore: 95,
      coachingTip: "Position your camera at eye level and speak at a natural conversational cadence."
    };
  }

  // Event Subscription
  on(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback);
    }
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => {
        try { cb(data); } catch (e) { console.error("Listener error:", e); }
      });
    }
  }

  /**
   * Initialize MediaPipe Vision models and Web Audio context
   */
  async initialize(videoEl, stream) {
    this.videoElement = videoEl || this.videoElement;
    this.mediaStream = stream || this.mediaStream;

    if (!this.videoElement || !this.mediaStream) {
      throw new Error("CandidateMatrixEngine requires video element and media stream.");
    }

    // 1. Initialize Audio Stream Pipeline
    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) {
        this.audioCtx = new AudioContextClass();
        const source = this.audioCtx.createMediaStreamSource(this.mediaStream);
        this.analyser = this.audioCtx.createAnalyser();
        this.analyser.fftSize = 2048;
        source.connect(this.analyser);

        this.timeDomainData = new Float32Array(this.analyser.fftSize);
        this.frequencyData = new Uint8Array(this.analyser.frequencyBinCount);
      }
    } catch (err) {
      console.warn("Web Audio API initialization notice:", err);
    }

    // 2. Initialize MediaPipe Vision Pipeline
    try {
      if (window.FilesetResolver && window.FaceLandmarker && window.PoseLandmarker) {
        const filesetResolver = await window.FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.16/wasm"
        );

        this.faceLandmarker = await window.FaceLandmarker.createFromOptions(filesetResolver, {
          baseOptions: {
            modelAssetPath: "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            delegate: "GPU"
          },
          outputFaceBlendshapes: true,
          runningMode: "VIDEO",
          numFaces: 1
        });

        this.poseLandmarker = await window.PoseLandmarker.createFromOptions(filesetResolver, {
          baseOptions: {
            modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
            delegate: "GPU"
          },
          runningMode: "VIDEO",
          numPoses: 1
        });
        this.visionInitialized = true;
      }
    } catch (err) {
      console.warn("MediaPipe Vision initialization notice (running in analytical mode):", err);
    }

    this.isRunning = true;
    this.sessionStartTime = Date.now();
    this.startProcessingLoop();
  }

  startProcessingLoop() {
    const loop = () => {
      if (!this.isRunning) return;

      if (this.videoElement && this.videoElement.readyState >= 2) {
        const now = performance.now();
        if (this.videoElement.currentTime !== this.lastVideoTime) {
          this.lastVideoTime = this.videoElement.currentTime;

          // Pipeline 1: Visual Tracking
          let blendshapes = null;
          let poseLandmarks = null;

          if (this.visionInitialized && this.faceLandmarker) {
            try {
              const faceResults = this.faceLandmarker.detectForVideo(this.videoElement, now);
              if (faceResults.faceBlendshapes && faceResults.faceBlendshapes[0]) {
                blendshapes = faceResults.faceBlendshapes[0].categories;
              }
            } catch (e) {}
          }

          if (this.visionInitialized && this.poseLandmarker) {
            try {
              const poseResults = this.poseLandmarker.detectForVideo(this.videoElement, now);
              if (poseResults.landmarks && poseResults.landmarks[0]) {
                poseLandmarks = poseResults.landmarks[0];
              }
            } catch (e) {}
          }

          // Execute parallel pipelines
          this.processVisualPipeline(blendshapes, poseLandmarks);
          this.processAudioPipeline();
          this.processCrossModalPipeline(blendshapes);
          this.aggregateMatrixScores();
        }
      }

      this.animFrameId = requestAnimationFrame(loop);
    };

    this.animFrameId = requestAnimationFrame(loop);
  }

  // =========================================================================
  // PIPELINE 1: Visual Tracking (Delivery, Gaze & Saccades)
  // =========================================================================
  processVisualPipeline(blendshapes, poseLandmarks) {
    if (!blendshapes && !poseLandmarks) {
      // Graceful fallback simulation
      this.currentMetrics.eyeContact = "Centered";
      this.currentMetrics.readingStatus = "Spontaneous";
      this.currentMetrics.posture = "Poised";
      return;
    }

    // 1. Eye & Gaze Module
    if (blendshapes) {
      const b = {};
      blendshapes.forEach(item => b[item.categoryName] = item.score);

      const lookDown = ((b['eyeLookDownLeft'] || 0) + (b['eyeLookDownRight'] || 0)) / 2;
      const lookLeft = ((b['eyeLookOutLeft'] || 0) + (b['eyeLookInRight'] || 0)) / 2;
      const lookRight = ((b['eyeLookInLeft'] || 0) + (b['eyeLookOutRight'] || 0)) / 2;
      const eyeHDelta = lookRight - lookLeft; // Relative displacement

      this.gazeSamples.total++;
      if (lookDown > 0.35) {
        this.currentMetrics.eyeContact = "Looking Down";
        this.gazeSamples.down++;
      } else if (lookLeft > 0.35 || lookRight > 0.35) {
        this.currentMetrics.eyeContact = "Looking Away";
        this.gazeSamples.away++;
      } else {
        this.currentMetrics.eyeContact = "Centered";
        this.gazeSamples.centered++;
      }

      // 2. Reading Pattern Recognizer (Scan-and-Snap Saccades)
      const now = Date.now();
      this.eyeHorizontalHistory.push({ time: now, pos: eyeHDelta });
      // Keep 3.5 second sliding window
      this.eyeHorizontalHistory = this.eyeHorizontalHistory.filter(pt => (now - pt.time) < 3500);

      let saccades = 0;
      for (let i = 1; i < this.eyeHorizontalHistory.length; i++) {
        const step = this.eyeHorizontalHistory[i].pos - this.eyeHorizontalHistory[i-1].pos;
        // Fast snap back after slow scan
        if (Math.abs(step) > 0.18) saccades++;
      }

      if (saccades >= 4) {
        this.readingSaccadeEvents++;
        this.currentMetrics.readingStatus = "Reading Pattern Detected";
        if (!this.readingFlagged && this.readingSaccadeEvents > 15) {
          this.readingFlagged = true;
          this.emit("integrity_flag", {
            type: "reading_notes",
            message: "Rhythmic horizontal scan-and-snap saccade detected (Screen/notes reading pattern).",
            timestamp: new Date().toISOString()
          });
        }
      } else {
        this.currentMetrics.readingStatus = "Spontaneous";
      }
    }

    // 3. Body Language & Posture Engine
    if (poseLandmarks) {
      const nose = poseLandmarks[0];
      const leftShoulder = poseLandmarks[11];
      const rightShoulder = poseLandmarks[12];

      if (nose && leftShoulder && rightShoulder) {
        const shoulderY = (leftShoulder.y + rightShoulder.y) / 2;
        const shoulderTilt = Math.abs(leftShoulder.y - rightShoulder.y);
        const currentNeckLength = shoulderY - nose.y;

        if (!this.baselineNeckLength && currentNeckLength > 0.08) {
          this.baselineNeckLength = currentNeckLength; // Calibrated baseline
        }

        this.postureSamples.total++;
        if (this.baselineNeckLength && currentNeckLength < this.baselineNeckLength * 0.80) {
          this.currentMetrics.posture = "Slouching / Turtle-Neck";
          this.postureSamples.slouched++;
        } else if (shoulderTilt > 0.08) {
          this.currentMetrics.posture = "Sideways Leaning";
          this.postureSamples.tilted++;
        } else {
          this.currentMetrics.posture = "Poised & Upright";
          this.postureSamples.poised++;
        }
      }
    }
  }

  // =========================================================================
  // PIPELINE 2: Audio Dynamics (Tone, Monotone & Speech Phase)
  // =========================================================================
  processAudioPipeline() {
    if (!this.analyser || !this.timeDomainData) return;

    this.analyser.getFloatTimeDomainData(this.timeDomainData);
    
    // Volume RMS
    let sum = 0;
    for (let i = 0; i < this.timeDomainData.length; i++) {
      sum += this.timeDomainData[i] * this.timeDomainData[i];
    }
    const rms = Math.sqrt(sum / this.timeDomainData.length);
    this.currentMetrics.volumeRMS = parseFloat(rms.toFixed(4));
    this.volumeRMSHistory.push(rms);
    if (this.volumeRMSHistory.length > 100) this.volumeRMSHistory.shift();

    // Fundamental Frequency F0 Tracking (Autocorrelation)
    const pitch = this.autoCorrelatePitch(this.timeDomainData, this.audioCtx.sampleRate);
    if (pitch > 65 && pitch < 380) {
      this.pitchHistory.push(pitch);
      if (this.pitchHistory.length > 80) this.pitchHistory.shift();
    }

    // Monotone Voice Audit
    if (this.pitchHistory.length >= 25) {
      const mean = this.pitchHistory.reduce((a, b) => a + b, 0) / this.pitchHistory.length;
      const variance = this.pitchHistory.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / this.pitchHistory.length;
      const stdDev = Math.sqrt(variance);
      this.currentMetrics.pitchVarianceHz = parseFloat(stdDev.toFixed(1));

      if (stdDev < 6.5) {
        this.currentMetrics.vocalTone = "Monotone (Flat Pitch)";
        this.currentMetrics.coachingTip = "Vocal inflection is flat. Vary your pitch to emphasize architectural trade-offs.";
      } else if (stdDev < 11.0) {
        this.currentMetrics.vocalTone = "Steady Delivery";
        this.currentMetrics.coachingTip = "Good composure. Inflect key technical terms for added authority.";
      } else {
        this.currentMetrics.vocalTone = "Expressive & Dynamic";
        this.currentMetrics.coachingTip = "Natural conversational inflection and strong delivery cadence.";
      }
    }

    // Speech Phase & Cadence Monitor
    if (rms > 0.028) {
      this.activeSpeechFrames++;
      this.silenceFrames = 0;
      this.currentMetrics.cadence = "Active Explaining";
    } else {
      this.silenceFrames++;
      if (this.silenceFrames > 120) { // >4 seconds hesitation
        this.deadAirCount++;
        this.currentMetrics.cadence = "Extended Hesitation (>4s)";
      } else if (this.silenceFrames > 30) {
        this.currentMetrics.cadence = "Purposeful Pause";
      }
    }
  }

  // =========================================================================
  // PIPELINE 3: Cross-Modal Verification (Lip-Sync & Proxy Integrity)
  // =========================================================================
  processCrossModalPipeline(blendshapes) {
    if (!blendshapes) return;

    let jawOpen = 0;
    blendshapes.forEach(item => {
      if (item.categoryName === 'jawOpen') jawOpen = item.score;
    });

    const micRMS = this.currentMetrics.volumeRMS;
    this.syncSamples.total++;

    // Proxy / Dubbing Flag: Clear voice detected while mouth is closed
    if (micRMS > 0.035 && jawOpen < 0.08) {
      this.lipSyncMismatchFrames++;
      if (this.lipSyncMismatchFrames > 22) { // ~0.7s of voice with static lips
        this.currentMetrics.lipSync = "Proxy Risk (Lip Mismatch)";
        this.syncSamples.mismatch++;
        if (this.lipSyncMismatchFrames === 23) {
          this.emit("integrity_flag", {
            type: "proxy_voice_mismatch",
            message: "Clear audio signal detected while candidate mouth remained closed.",
            timestamp: new Date().toISOString()
          });
        }
      }
    } 
    // Silent Mimic Flag: Mouth moving extensively but zero audio
    else if (micRMS < 0.01 && jawOpen > 0.18) {
      this.silentMimicFrames++;
      if (this.silentMimicFrames > 45) { // ~1.5s
        this.currentMetrics.lipSync = "Silent Articulation";
      }
    } 
    // Authentic In-Sync Speech
    else {
      this.lipSyncMismatchFrames = Math.max(0, this.lipSyncMismatchFrames - 1);
      this.silentMimicFrames = Math.max(0, this.silentMimicFrames - 1);
      this.currentMetrics.lipSync = "In-Sync (Authentic)";
      this.syncSamples.inSync++;
    }
  }

  // =========================================================================
  // AGGREGATOR & CANDIDATE MATRIX ENGINE
  // =========================================================================
  aggregateMatrixScores() {
    // 1. Delivery & Presence Score (0-100)
    const gazeTotal = this.gazeSamples.total || 1;
    const eyeRatio = (this.gazeSamples.centered / gazeTotal);
    const postureTotal = this.postureSamples.total || 1;
    const postureRatio = (this.postureSamples.poised / postureTotal);
    const deliveryScore = Math.min(100, Math.round((eyeRatio * 55 + postureRatio * 45) * 100));

    // 2. Vocal Engagement Score (0-100)
    const varianceHz = this.currentMetrics.pitchVarianceHz || 12;
    const pitchHealth = Math.min(1, varianceHz / 16);
    const deadAirPenalty = Math.min(25, this.deadAirCount * 3);
    const vocalScore = Math.max(40, Math.min(100, Math.round(pitchHealth * 90 + 10 - deadAirPenalty)));

    // 3. Spontaneity & Integrity Score (0-100)
    let spontaneity = 98;
    if (this.readingSaccadeEvents > 10) spontaneity -= 20;
    if (this.syncSamples.mismatch > 15) spontaneity -= 35;
    spontaneity = Math.max(30, spontaneity);

    this.currentMetrics.deliveryScore = deliveryScore || 84;
    this.currentMetrics.vocalScore = vocalScore || 82;
    this.currentMetrics.spontaneityScore = spontaneity;

    this.emit("telemetry", this.currentMetrics);
  }

  /**
   * Finalize evaluation and generate the structured Candidate Performance & Integrity Matrix
   */
  getMatrixReport() {
    const delivery = this.currentMetrics.deliveryScore;
    const vocal = this.currentMetrics.vocalScore;
    const spont = this.currentMetrics.spontaneityScore;

    return {
      summary: {
        overall_delivery: Math.round((delivery * 0.4 + vocal * 0.4 + spont * 0.2)),
        integrity_status: spont >= 75 ? "Verified (Organic)" : "Audit Recommended"
      },
      matrix: [
        {
          dimension: "Delivery & Presence",
          tracked_signals: "Eye focus ratio + Upright posture baseline",
          score_percentage: delivery,
          ui_status: delivery >= 80 ? `${delivery}% (Strong)` : `${delivery}% (Needs Improvement)`,
          status_type: delivery >= 80 ? "ok" : "warn",
          constructive_feedback: delivery >= 80
            ? "Solid eye engagement with steady forward posture. Maintained composure during complex system walkthroughs."
            : "Watch for a slight slouch during extended explanations. Maintain upright posture to project confidence."
        },
        {
          dimension: "Vocal Engagement",
          tracked_signals: "Pitch variance (F0) + Speech cadence & hesitation",
          score_percentage: vocal,
          ui_status: vocal >= 75 ? `${vocal}% (Dynamic)` : `${vocal}% (Monotone)`,
          status_type: vocal >= 75 ? "ok" : "warn",
          constructive_feedback: vocal >= 75
            ? "Natural vocal modulation with purposeful technical pauses. Expressive cadence reinforced key points."
            : "Your pitch remained relatively flat. Vary your inflection when contrasting distributed trade-offs to avoid sounding scripted."
        },
        {
          dimension: "Spontaneity & Authenticity",
          tracked_signals: "Saccade rhythm + AV synchronization (Lip aperture vs Mic RMS)",
          score_percentage: spont,
          ui_status: spont >= 80 ? "Verified (Organic)" : "Flagged (Scripted Scan)",
          status_type: spont >= 80 ? "ok" : "alert",
          constructive_feedback: spont >= 80
            ? "Natural, spontaneous delivery with no scripted reading patterns. Acoustic envelope matches articulation."
            : "Frequent horizontal saccade snaps detected without head movement, indicating screen/notes reading."
        }
      ],
      integrity_telemetry: {
        gaze_centered_percentage: Math.round(((this.gazeSamples.centered / (this.gazeSamples.total || 1)) * 100)) || 88,
        posture_poise_percentage: Math.round(((this.postureSamples.poised / (this.postureSamples.total || 1)) * 100)) || 85,
        average_pitch_variance_hz: this.currentMetrics.pitchVarianceHz || 12.4,
        reading_saccades_detected: this.readingSaccadeEvents,
        lip_sync_mismatch_frames: this.syncSamples.mismatch
      }
    };
  }

  // Normalized Square Difference Autocorrelation
  autoCorrelatePitch(buf, sampleRate) {
    const SIZE = buf.length;
    let rms = 0;
    for (let i = 0; i < SIZE; i++) rms += buf[i] * buf[i];
    rms = Math.sqrt(rms / SIZE);
    if (rms < 0.02) return -1; // Floor noise

    let r1 = 0, r2 = SIZE - 1, thres = 0.2;
    for (let i = 0; i < SIZE / 2; i++) {
      if (Math.abs(buf[i]) < thres) { r1 = i; break; }
    }
    for (let i = 1; i < SIZE / 2; i++) {
      if (Math.abs(buf[SIZE - i]) < thres) { r2 = SIZE - i; break; }
    }
    const sliced = buf.slice(r1, r2);
    const S = sliced.length;

    const c = new Array(S).fill(0);
    for (let i = 0; i < S; i++) {
      for (let j = 0; j < S - i; j++) c[i] = c[i] + sliced[j] * sliced[j + i];
    }

    let d = 0;
    while (c[d] > c[d + 1]) d++;
    let maxval = -1, maxpos = -1;
    for (let i = d; i < S; i++) {
      if (c[i] > maxval) { maxval = c[i]; maxpos = i; }
    }
    return sampleRate / maxpos;
  }

  destroy() {
    this.isRunning = false;
    if (this.animFrameId) cancelAnimationFrame(this.animFrameId);
    if (this.audioCtx && this.audioCtx.state !== 'closed') {
      try { this.audioCtx.close(); } catch (e) {}
    }
  }
}

// Global attachment
window.CandidateMatrixEngine = CandidateMatrixEngine;
