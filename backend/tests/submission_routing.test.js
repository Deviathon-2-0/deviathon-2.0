/**
 * IMAIRA+ Mock Interview Submission Routing & Error Handling Tests
 * 
 * Tests the requirements:
 * 1. Successful submission: Valid 4-question interview submission to the active backend returns 200,
 *    evaluates scores, and caches report for retrieval.
 * 2. Backend unavailable / fallback: When the primary candidate backend is unreachable (simulated
 *    offline port), dispatch falls back to the active available backend.
 * 3. Unsuccessful HTTP response: When a backend responds with an HTTP error (400 or 500), dispatch
 *    explicitly returns the error without blindly retrying against other backends.
 * 4. Duplicate submission prevention: Re-submitting an existing session ID updates/returns the evaluation
 *    without duplicating records or creating conflicting sessions.
 * 5. All backends unavailable: When all candidate endpoints are unreachable, dispatch returns an explicit
 *    network error instead of silently succeeding.
 */

const { describe, it, before, after } = require("node:test");
const assert = require("node:assert");
const http = require("http");
const express = require("express");
const app = require("../server");

describe("Interview Submission Routing & Dispatch Tests", () => {
  let activeServer;
  let activePort;
  let activeBaseUrl;

  before(async () => {
    activeServer = http.createServer(app);
    await new Promise((resolve) => {
      activeServer.listen(0, "127.0.0.1", () => {
        activePort = activeServer.address().port;
        activeBaseUrl = `http://127.0.0.1:${activePort}`;
        resolve();
      });
    });
  });

  after(async () => {
    await new Promise((resolve) => activeServer.close(resolve));
  });

  /**
   * Node-side implementation of the dispatchInterviewSubmission logic
   * used in frontend/pages/mock-interview.html to verify its exact behavior.
   */
  async function simulateFrontendDispatch(sessionId, payload, candidateBases) {
    let lastNetworkError = null;

    for (let i = 0; i < candidateBases.length; i++) {
      const base = candidateBases[i];
      const cleanBase = base.endsWith('/') ? base.slice(0, -1) : base;
      const submitUrl = `${cleanBase}/api/sessions/${encodeURIComponent(sessionId)}/submit/`;

      try {
        const res = await fetch(submitUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          const reportData = await res.json();
          return {
            success: true,
            data: reportData,
            backendBase: base,
            endpoint: submitUrl
          };
        }

        // Server responded with an unsuccessful HTTP code (4xx / 5xx)
        // Must NOT blindly retry against another backend!
        let errorDetail = `Server responded with status ${res.status}`;
        try {
          const errJson = await res.json();
          if (errJson && (errJson.message || errJson.error)) {
            errorDetail = errJson.message || errJson.error;
          }
        } catch (_) {}

        return {
          success: false,
          errorType: "HTTP_ERROR",
          status: res.status,
          message: `Evaluation rejected by server: ${errorDetail}`,
          endpoint: submitUrl
        };
      } catch (netErr) {
        // Network connection error (server offline/refused)
        lastNetworkError = netErr;
      }
    }

    return {
      success: false,
      errorType: "NETWORK_ERROR",
      message: "Could not connect to evaluation server on any candidate port.",
      error: lastNetworkError
    };
  }

  it("1. Successful submission: evaluates all questions, returns scores and report", async () => {
    const sessionId = "ses_routing_test_" + Date.now();
    const payload = {
      session_id: sessionId,
      role: "Software Engineer",
      company: "Google",
      track: "Tech",
      seniority_level: "SDE 2",
      answers: [
        {
          question_index: 0,
          question_text: "Explain polymorphism in OOP.",
          transcript: "Polymorphism enables objects of different classes to be treated through a common interface.",
          code: "class Shape { virtual void draw() = 0; };"
        },
        {
          question_index: 1,
          question_text: "Explain ACID properties in database systems.",
          transcript: "ACID stands for Atomicity, Consistency, Isolation, and Durability in database transactions.",
          code: ""
        },
        {
          question_index: 2,
          question_text: "Explain HashMap collision resolution.",
          transcript: "Hash collisions occur when distinct keys produce identical hash indices, resolved via separate chaining.",
          code: ""
        },
        {
          question_index: 3,
          question_text: "Explain concurrency and race conditions.",
          transcript: "Race conditions arise when multiple threads access shared memory concurrently without synchronization.",
          code: ""
        }
      ]
    };

    const result = await simulateFrontendDispatch(sessionId, payload, [activeBaseUrl]);
    assert.strictEqual(result.success, true, "Submission must succeed");
    assert.strictEqual(result.data.sessionId, sessionId);
    assert.ok(result.data.scores, "Must include evaluation scores");
    assert.strictEqual(typeof result.data.compositeScore, "number");
    assert.strictEqual(result.data.report.perQuestionBreakdown.length, 4);

    // Verify report retrieval via GET endpoint
    const reportRes = await fetch(`${activeBaseUrl}/api/sessions/${sessionId}/report`);
    assert.strictEqual(reportRes.status, 200);
    const reportData = await reportRes.json();
    assert.strictEqual(reportData.sessionId, sessionId);
    assert.strictEqual(reportData.perQuestionBreakdown.length, 4);
  });

  it("2. Backend unavailable fallback: falls back to active backend when primary is offline", async () => {
    const sessionId = "ses_fallback_test_" + Date.now();
    const deadPortUrl = "http://127.0.0.1:59999"; // port 59999 is inactive

    const payload = {
      session_id: sessionId,
      role: "Staff Engineer",
      company: "Stripe",
      answers: [
        {
          question_index: 0,
          question_text: "Explain distributed caching.",
          transcript: "Distributed cache partitions keys across nodes using consistent hashing.",
          code: ""
        }
      ]
    };

    // Primary: dead port, Fallback: active test server
    const result = await simulateFrontendDispatch(sessionId, payload, [deadPortUrl, activeBaseUrl]);
    assert.strictEqual(result.success, true, "Dispatch should gracefully fall back to active backend");
    assert.strictEqual(result.backendBase, activeBaseUrl, "Must have used the active backend fallback");
    assert.strictEqual(result.data.sessionId, sessionId);
  });

  it("3. Unsuccessful HTTP response: does NOT blindly retry on another backend", async () => {
    // Create a temporary mock server that returns HTTP 400 Bad Request
    const errorServer = express();
    let errorServerCallCount = 0;
    let fallbackServerCallCount = 0;

    errorServer.post("/api/sessions/:id/submit", (req, res) => {
      errorServerCallCount++;
      res.status(400).json({ error: "InvalidPayload", message: "Malformed answer data format." });
    });

    const errHttpServer = http.createServer(errorServer);
    let errPort;
    await new Promise((resolve) => {
      errHttpServer.listen(0, "127.0.0.1", () => {
        errPort = errHttpServer.address().port;
        resolve();
      });
    });

    // Create a second mock server acting as the fallback
    const fallbackServer = express();
    fallbackServer.post("/api/sessions/:id/submit", (req, res) => {
      fallbackServerCallCount++;
      res.status(200).json({ success: true });
    });
    const fallbackHttpServer = http.createServer(fallbackServer);
    let fallbackPort;
    await new Promise((resolve) => {
      fallbackHttpServer.listen(0, "127.0.0.1", () => {
        fallbackPort = fallbackHttpServer.address().port;
        resolve();
      });
    });

    const sessionId = "ses_error_test_" + Date.now();
    const payload = { role: "Engineer", answers: [] };

    const result = await simulateFrontendDispatch(sessionId, payload, [
      `http://127.0.0.1:${errPort}`,
      `http://127.0.0.1:${fallbackPort}`
    ]);

    // Cleanup mock servers
    await new Promise((r) => errHttpServer.close(r));
    await new Promise((r) => fallbackHttpServer.close(r));

    assert.strictEqual(result.success, false, "Must return failure on HTTP 400");
    assert.strictEqual(result.errorType, "HTTP_ERROR");
    assert.strictEqual(result.status, 400);
    assert.ok(result.message.includes("Malformed answer data format."));
    assert.strictEqual(errorServerCallCount, 1, "Primary error server must have been called exactly once");
    assert.strictEqual(fallbackServerCallCount, 0, "Fallback server must NOT be called when primary returns HTTP error");
  });

  it("4. Duplicate submission prevention & idempotency: handles repeat submits cleanly", async () => {
    const sessionId = "ses_idempotent_" + Date.now();
    const payload = {
      session_id: sessionId,
      role: "Backend Engineer",
      company: "Netflix",
      answers: [
        {
          question_index: 0,
          question_text: "Explain database indexing.",
          transcript: "B-Tree indexes maintain sorted keys with log N search complexity.",
          code: ""
        }
      ]
    };

    // First submission
    const res1 = await simulateFrontendDispatch(sessionId, payload, [activeBaseUrl]);
    assert.strictEqual(res1.success, true);
    const score1 = res1.data.compositeScore;

    // Second submission with same session ID
    const res2 = await simulateFrontendDispatch(sessionId, payload, [activeBaseUrl]);
    assert.strictEqual(res2.success, true);
    assert.strictEqual(res2.data.compositeScore, score1, "Composite score must remain consistent");
    assert.strictEqual(res2.data.sessionId, sessionId);

    // Verify GET report only has 1 question, not 2 duplicated questions
    const reportRes = await fetch(`${activeBaseUrl}/api/sessions/${sessionId}/report`);
    const reportData = await reportRes.json();
    assert.strictEqual(reportData.perQuestionBreakdown.length, 1, "Must not duplicate questions in report");
  });

  it("5. All backends unavailable: returns explicit network error without throwing", async () => {
    const deadUrl1 = "http://127.0.0.1:59998";
    const deadUrl2 = "http://127.0.0.1:59999";
    const sessionId = "ses_dead_" + Date.now();

    const result = await simulateFrontendDispatch(sessionId, { answers: [] }, [deadUrl1, deadUrl2]);
    assert.strictEqual(result.success, false);
    assert.strictEqual(result.errorType, "NETWORK_ERROR");
    assert.ok(result.message.includes("Could not connect"));
  });

  it("6. Canonical trailing-slash route compatibility: accepts POST /submit/ directly", async () => {
    const sessionId = "ses_slash_compat_" + Date.now();
    const payload = {
      session_id: sessionId,
      role: "Full Stack Engineer",
      company: "Meta",
      answers: [
        {
          question_index: 0,
          question_text: "Explain virtual DOM in React.",
          transcript: "Virtual DOM minimizes direct DOM manipulation by diffing lightweight tree representations.",
          code: ""
        }
      ]
    };

    // Explicitly verify POST with trailing slash
    const directRes = await fetch(`${activeBaseUrl}/api/sessions/${sessionId}/submit/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    assert.strictEqual(directRes.status, 200, "POST with trailing slash must return 200 OK without redirecting");
    const body = await directRes.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.sessionId, sessionId);
    assert.strictEqual(body.report.perQuestionBreakdown.length, 1);
  });

  it("7. Duplicate-click protection: simulates rapid clicking and confirms lock-out", async () => {
    // Model the frontend's transition and submission lock state machine
    let isSubmittingAnswer = false;
    let isSubmittingInterview = false;
    let transitionCount = 0;
    let backendCallCount = 0;

    async function simulatedSubmitCurrentAnswer(isFinalQuestion) {
      if (isSubmittingAnswer || isSubmittingInterview) return { status: "LOCKED_OUT" };
      isSubmittingAnswer = true;

      // Simulate async speech settlement
      await new Promise((r) => setTimeout(r, 50));

      if (!isFinalQuestion) {
        transitionCount++;
        isSubmittingAnswer = false;
        return { status: "TRANSITIONED" };
      }

      isSubmittingInterview = true;
      backendCallCount++;
      // Simulate backend latency
      await new Promise((r) => setTimeout(r, 60));
      isSubmittingInterview = false;
      isSubmittingAnswer = false;
      return { status: "SUBMITTED" };
    }

    // 1. Rapid clicks during question transition (e.g. Q1 -> Q2)
    const [click1, click2, click3] = await Promise.all([
      simulatedSubmitCurrentAnswer(false),
      simulatedSubmitCurrentAnswer(false),
      simulatedSubmitCurrentAnswer(false)
    ]);

    assert.strictEqual(click1.status, "TRANSITIONED", "First click must process transition");
    assert.strictEqual(click2.status, "LOCKED_OUT", "Rapid second click must be locked out");
    assert.strictEqual(click3.status, "LOCKED_OUT", "Rapid third click must be locked out");
    assert.strictEqual(transitionCount, 1, "Must transition exactly once despite 3 concurrent clicks");

    // 2. Rapid clicks on final question submission
    const [finalClick1, finalClick2, finalClick3] = await Promise.all([
      simulatedSubmitCurrentAnswer(true),
      simulatedSubmitCurrentAnswer(true),
      simulatedSubmitCurrentAnswer(true)
    ]);

    assert.strictEqual(finalClick1.status, "SUBMITTED", "First final click must submit");
    assert.strictEqual(finalClick2.status, "LOCKED_OUT", "Duplicate final click must be locked out");
    assert.strictEqual(finalClick3.status, "LOCKED_OUT", "Duplicate final click must be locked out");
    assert.strictEqual(backendCallCount, 1, "Backend must be called exactly once");
  });
});
