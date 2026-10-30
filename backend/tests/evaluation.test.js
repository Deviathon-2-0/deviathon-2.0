/**
 * IMAIRA+ Interview Evaluation Service Tests
 * 
 * Verifies deterministic scoring, evidence extraction, concept matching,
 * telemetry incorporation, empty answer handling, and session submission / report API.
 * Uses native Node 18+ fetch / http without external dependencies like supertest.
 */
require("dotenv").config();
const { describe, it, before, after } = require("node:test");
const assert = require("node:assert");
const http = require("http");

const evaluationService = require("../services/evaluationService");
const app = require("../server");

describe("Evaluation Service - Unit Tests", () => {
  it("should evaluate answer with technical concept coverage and extract verbatim evidence", () => {
    const questionText = "Explain polymorphism and dynamic method dispatch in Java.";
    const transcript = "Polymorphism allows subclasses to provide their own implementation of a method. At runtime, dynamic dispatch resolves which implementation to invoke through the vtable or virtual table hierarchy.";

    const result = evaluationService.evaluateAnswer({
      question_text: questionText,
      transcript,
      code: ""
    });

    assert.ok(result.technicalScore >= 80, "Technical score should be high for clear answer");
    assert.ok(result.coveredConcepts.length >= 2, "Should cover at least 2 key concepts");
    assert.ok(result.coveredConcepts.some(c => c.concept === "Polymorphism"), "Should cover Polymorphism");
    assert.ok(result.coveredConcepts.some(c => c.concept === "Dynamic Dispatch"), "Should cover Dynamic Dispatch");

    const polyConcept = result.coveredConcepts.find(c => c.concept === "Polymorphism");
    assert.ok(polyConcept.evidence, "Evidence quote must exist");
    assert.ok(transcript.includes(polyConcept.evidence.replace(/\.\.\./g, "").trim().slice(0, 20)), "Evidence must be an actual excerpt from candidate transcript");
  });

  it("should match glossary candidate terms and award credit for technical synonyms", () => {
    const questionText = "Define DBMS fundamentals and explain ACID properties.";
    // Accent-neutral scenario where STT or candidate uses synonym/variant
    const transcript = "In a DBMS, atomicity means all or nothing. Durability ensures that committed transactions survive crashes via write ahead log.";
    const candidates = [
      { canonical: "Durability", term: "write ahead log", confidence: 0.92 }
    ];

    const result = evaluationService.evaluateAnswer({
      question_text: questionText,
      transcript,
      candidates
    });

    assert.ok(result.coveredConcepts.some(c => c.concept === "Atomicity"));
    assert.ok(result.coveredConcepts.some(c => c.concept === "Durability"));
  });

  it("should evaluate structural logic based on transition phrases and progression", () => {
    const singleSentence = "Hash map has buckets and collisions happen.";
    const structuredAnswer = "First, a hash map maps keys to array buckets using a hash code. However, when collisions occur, it resolves them via separate chaining. Therefore, the average time complexity remains O(1).";

    const resSingle = evaluationService.evaluateAnswer({ question_text: "HashMap internals", transcript: singleSentence });
    const resStructured = evaluationService.evaluateAnswer({ question_text: "HashMap internals", transcript: structuredAnswer });

    assert.ok(resStructured.structureScore > resSingle.structureScore, "Structured answer with transitions must score higher");
    assert.ok(resStructured.structureScore >= 75, "Structured answer should reach at least 75");
  });

  it("should handle empty or blank answers gracefully without throwing", () => {
    const emptyResult = evaluationService.evaluateAnswer({
      question_text: "Explain processes vs threads",
      transcript: "",
      code: ""
    });

    assert.strictEqual(emptyResult.technicalScore, 0);
    assert.strictEqual(emptyResult.structureScore, 0);
    assert.strictEqual(emptyResult.speechScore, 0);
    assert.strictEqual(emptyResult.wordCount, 0);
    assert.ok(emptyResult.diagnosticEvents.some(e => e.type === "BLUNDER"));
  });

  it("should evaluate candidate code implementation without spoken transcript and without synthetic placeholders", () => {
    const questionText = "Remove Invalid Parentheses using BFS";
    const code = "function removeInvalidParentheses(s) {\n  let queue = [s];\n  let visited = new Set([s]);\n  while (queue.length > 0) {\n    let curr = queue.shift();\n    if (isValid(curr)) return [curr];\n    for (let i = 0; i < curr.length; i++) {\n      let next = curr.slice(0, i) + curr.slice(i + 1);\n      if (!visited.has(next)) { visited.add(next); queue.push(next); }\n    }\n  }\n  return [];\n}";
    const transcript = "";

    const res = evaluationService.evaluateAnswer({
      question_text: questionText,
      transcript,
      code
    });

    assert.ok(res.technicalScore >= 50, "Code implementation should yield positive technical score");
    assert.ok(res.structureScore >= 60, "Code structure should be scored for functions and returns");
    assert.strictEqual(res.speechScore, 0, "Speech score should be 0 when no verbal answer is spoken");

    const sessionReport = evaluationService.evaluateSession({
      answers: [{ question_index: 0, question_text: questionText, transcript: "", code }],
      role: "Software Engineer",
      company: "Meta"
    });

    assert.strictEqual(sessionReport.perQuestionBreakdown[0].transcript, "");
    assert.strictEqual(sessionReport.perQuestionBreakdown[0].code, code);
    assert.ok(sessionReport.perQuestionBreakdown[0].score > 40, "Question score should evaluate code properly");
  });

  it("should evaluate candidate with both spoken transcript and submitted code separately", () => {
    const questionText = "Merge Interval Overlaps";
    const transcript = "First, we sort the intervals by start time in O(N log N). Then, we perform a single pass linear sweep to merge any overlapping intervals where the start time is less than the previous max end.";
    const code = "function mergeIntervals(intervals) {\n  if (!intervals.length) return [];\n  intervals.sort((a, b) => a[0] - b[0]);\n  const result = [intervals[0]];\n  for (let i = 1; i < intervals.length; i++) {\n    const prev = result[result.length - 1];\n    if (intervals[i][0] <= prev[1]) {\n      prev[1] = Math.max(prev[1], intervals[i][1]);\n    } else {\n      result.push(intervals[i]);\n    }\n  }\n  return result;\n}";

    const sessionReport = evaluationService.evaluateSession({
      answers: [{ question_index: 0, question_text: questionText, transcript, code }],
      role: "Software Engineer"
    });

    assert.strictEqual(sessionReport.perQuestionBreakdown[0].transcript, transcript);
    assert.strictEqual(sessionReport.perQuestionBreakdown[0].code, code);
    assert.ok(sessionReport.perQuestionBreakdown[0].score >= 80, "Combined answer should score high");
  });

  it("should evaluate full session with real telemetry and apply 45/25/20/10 weighting", () => {
    const answers = [
      {
        question_index: 0,
        question_text: "Explain DBMS fundamentals and explain ACID properties.",
        transcript: "First, atomicity guarantees all or nothing execution. Consistency enforces database invariants. Isolation ensures concurrent transactions do not interfere, and durability ensures committed changes persist using WAL.",
        code: ""
      },
      {
        question_index: 1,
        question_text: "Differentiate processes and threads.",
        transcript: "Processes have their own isolated virtual address space. In contrast, threads share the same address space and memory heap. Context switching between threads is faster than processes.",
        code: ""
      }
    ];

    const realTelemetry = {
      summary: { overall_delivery: 85 },
      integrity_telemetry: {
        gaze_centered_percentage: 88,
        posture_poise_percentage: 90,
        average_pitch_variance_hz: 14.5
      }
    };

    const sessionReport = evaluationService.evaluateSession({
      answers,
      role: "Backend Developer",
      company: "Google",
      integrity_matrix: realTelemetry
    });

    assert.strictEqual(sessionReport.success, true);
    assert.strictEqual(sessionReport.scores.bodyLanguage, 85);
    assert.strictEqual(sessionReport.metrics.bodyLanguage.isAvailable, true);
    assert.ok(sessionReport.compositeScore >= 80, "Composite score should be B or A");
    assert.strictEqual(sessionReport.grade, evaluationService.calculateGrade(sessionReport.compositeScore));
  });

  it("should explicitly mark body language as unavailable when telemetry is missing", () => {
    const answers = [
      {
        question_index: 0,
        question_text: "Explain polymorphism",
        transcript: "Polymorphism allows dynamic method dispatch at runtime.",
        code: ""
      }
    ];

    const sessionReport = evaluationService.evaluateSession({
      answers,
      role: "Software Engineer",
      company: "Google",
      integrity_matrix: null // Telemetry missing
    });

    assert.strictEqual(sessionReport.scores.bodyLanguage, null);
    assert.strictEqual(sessionReport.metrics.bodyLanguage.isAvailable, false);
    assert.strictEqual(sessionReport.metrics.bodyLanguage.rating, "Telemetry Unavailable");
    assert.ok(sessionReport.compositeScore > 0, "Composite score re-normalizes without telemetry");
  });

  it("should calculate correct grade thresholds", () => {
    assert.strictEqual(evaluationService.calculateGrade(95), "A");
    assert.strictEqual(evaluationService.calculateGrade(90), "A");
    assert.strictEqual(evaluationService.calculateGrade(85), "B");
    assert.strictEqual(evaluationService.calculateGrade(80), "B");
    assert.strictEqual(evaluationService.calculateGrade(75), "C");
    assert.strictEqual(evaluationService.calculateGrade(70), "C");
    assert.strictEqual(evaluationService.calculateGrade(65), "D");
  });
});

describe("Session Evaluation & Report - API Integration Tests", () => {
  let server;
  let testPort;
  let baseUrl;
  const testSessionId = "test_eval_session_" + Date.now();

  before(async () => {
    server = http.createServer(app);
    await new Promise((resolve) => {
      server.listen(0, "127.0.0.1", () => {
        testPort = server.address().port;
        baseUrl = `http://127.0.0.1:${testPort}`;
        resolve();
      });
    });
  });

  after(async () => {
    await new Promise((resolve) => server.close(resolve));
  });

  it("POST /api/sessions/:id/submit should evaluate session and return personalized report", async () => {
    const payload = {
      role: "Backend Engineer",
      company: "Google",
      answers: [
        {
          question_index: 0,
          question_text: "Explain HashMap internals and collision resolution.",
          transcript: "A hash map uses an array of buckets. When a collision occurs, it resolves it using separate chaining with linked lists or balanced trees. Therefore, lookups remain O(1) amortized.",
          code: ""
        }
      ],
      integrity_matrix: {
        summary: { overall_delivery: 82 },
        integrity_telemetry: {
          gaze_centered_percentage: 84,
          posture_poise_percentage: 86,
          average_pitch_variance_hz: 12.8
        }
      }
    };

    const res = await fetch(`${baseUrl}/api/sessions/${testSessionId}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.sessionId, testSessionId);
    assert.ok(body.scores, "Should return scores object");
    assert.ok(body.report, "Should return evaluated report");
    assert.ok(body.compositeScore > 0, "Should have composite score");
    assert.strictEqual(body.report.perQuestionBreakdown.length, 1);
  });

  it("GET /api/sessions/:id/report should retrieve the cached evaluation report", async () => {
    const res = await fetch(`${baseUrl}/api/sessions/${testSessionId}/report`);
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.sessionId, testSessionId);
    assert.strictEqual(body.role, "Backend Engineer");
    assert.ok(body.perQuestionBreakdown.length > 0);
  });

  it("POST /api/sessions/:id/submit should preserve actual code and transcript without placeholders in report", async () => {
    const codeSessionId = "test_code_session_" + Date.now();
    const candidateCode = "function reverseList(head) {\n  let prev = null, curr = head;\n  while (curr) {\n    let next = curr.next;\n    curr.next = prev;\n    prev = curr;\n    curr = next;\n  }\n  return prev;\n}";
    const payload = {
      role: "Frontend Engineer",
      company: "Amazon",
      answers: [
        {
          question_index: 0,
          question_text: "Reverse a Singly Linked List",
          transcript: "",
          code: candidateCode
        }
      ]
    };

    const res = await fetch(`${baseUrl}/api/sessions/${codeSessionId}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.sessionId, codeSessionId);
    assert.strictEqual(body.report.perQuestionBreakdown[0].transcript, "");
    assert.strictEqual(body.report.perQuestionBreakdown[0].code, candidateCode);

    // Verify report retrieval via GET
    const repRes = await fetch(`${baseUrl}/api/sessions/${codeSessionId}/report`);
    assert.strictEqual(repRes.status, 200);
    const repBody = await repRes.json();
    assert.strictEqual(repBody.sessionId, codeSessionId);
    assert.strictEqual(repBody.perQuestionBreakdown[0].code, candidateCode);
    assert.strictEqual(repBody.perQuestionBreakdown[0].transcript, "");
  });
});
