/**
 * IMAIRA+ End-to-End Multi-Question & Retake Verification Tests
 * 
 * Verifies:
 * 1. 4-question interview with distinct spoken answers for all 4 questions.
 * 2. All 4 exact transcripts appear in submission payload and report.
 * 3. Retake under a new session ID receives new answers without stale or cross-session leakage.
 * 4. Distinct session IDs do not collide or overwrite each other.
 * 5. Unknown session ID returns 404 without falling back to sample data.
 */

const { describe, it, before, after } = require("node:test");
const assert = require("node:assert");
const http = require("http");
const app = require("../server");

describe("Four-Question Interview & Retake Data Flow Tests", () => {
  let server;
  let baseUrl;

  before(async () => {
    server = http.createServer(app);
    await new Promise((resolve) => {
      server.listen(0, "127.0.0.1", () => {
        const port = server.address().port;
        baseUrl = `http://127.0.0.1:${port}`;
        resolve();
      });
    });
  });

  after(async () => {
    await new Promise((resolve) => server.close(resolve));
  });

  it("should capture and report all four spoken answers in a 4-question interview", async () => {
    const session1Id = "ses_interview_1_" + Date.now();

    const fourAnswers = [
      {
        question_index: 0,
        question_text: "Explain polymorphism and dynamic method dispatch in Java.",
        transcript: "First, polymorphism allows derived classes to override base class methods at runtime.",
        code: ""
      },
      {
        question_index: 1,
        question_text: "Define DBMS fundamentals and explain ACID properties.",
        transcript: "Second, in DBMS, atomicity ensures all operations succeed or the transaction rolls back.",
        code: ""
      },
      {
        question_index: 2,
        question_text: "Differentiate processes and threads.",
        transcript: "Third, processes have isolated address spaces whereas threads share memory.",
        code: ""
      },
      {
        question_index: 3,
        question_text: "Explain HashMap internals and collision resolution.",
        transcript: "Fourth, separate chaining resolves hash collisions using linked lists.",
        code: ""
      }
    ];

    const submitRes = await fetch(`${baseUrl}/api/sessions/${session1Id}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "Senior Software Engineer",
        company: "Google",
        answers: fourAnswers
      })
    });

    assert.strictEqual(submitRes.status, 200, "Submission must return 200");
    const submitBody = await submitRes.json();
    assert.strictEqual(submitBody.sessionId, session1Id);
    assert.strictEqual(submitBody.report.perQuestionBreakdown.length, 4, "Must have exactly 4 questions");

    // Verify all 4 transcripts in the submit response
    for (let i = 0; i < 4; i++) {
      assert.strictEqual(
        submitBody.report.perQuestionBreakdown[i].transcript,
        fourAnswers[i].transcript,
        `Question ${i + 1} transcript must match submitted speech verbatim in submit response`
      );
    }

    // Verify all 4 transcripts in the GET /api/sessions/:id/report response
    const getRes = await fetch(`${baseUrl}/api/sessions/${session1Id}/report`);
    assert.strictEqual(getRes.status, 200, "Report fetch must return 200");
    const getBody = await getRes.json();
    assert.strictEqual(getBody.sessionId, session1Id);
    assert.strictEqual(getBody.perQuestionBreakdown.length, 4);

    for (let i = 0; i < 4; i++) {
      assert.strictEqual(
        getBody.perQuestionBreakdown[i].transcript,
        fourAnswers[i].transcript,
        `Question ${i + 1} transcript must match submitted speech verbatim in report GET endpoint`
      );
    }
  });

  it("should cleanly support retaking the interview under a new session ID with distinct answers", async () => {
    const session2Id = "ses_interview_retake_" + Date.now();

    const retakeAnswers = [
      {
        question_index: 0,
        question_text: "Explain in-memory caching with Redis.",
        transcript: "Retake answer one: Redis uses a single threaded event loop with in memory key-value storage.",
        code: ""
      },
      {
        question_index: 1,
        question_text: "Explain CAP theorem trade-offs.",
        transcript: "Retake answer two: CAP theorem balances consistency and availability during network partition.",
        code: ""
      },
      {
        question_index: 2,
        question_text: "Explain TCP handshake and reliability.",
        transcript: "Retake answer three: TCP provides reliable byte stream with three way handshake.",
        code: ""
      },
      {
        question_index: 3,
        question_text: "Explain Raft consensus mechanism.",
        transcript: "Retake answer four: Raft consensus uses leader election and log replication.",
        code: ""
      }
    ];

    const retakeSubmit = await fetch(`${baseUrl}/api/sessions/${session2Id}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: "Staff Engineer",
        company: "Stripe",
        answers: retakeAnswers
      })
    });

    assert.strictEqual(retakeSubmit.status, 200);
    const retakeBody = await retakeSubmit.json();
    assert.strictEqual(retakeBody.sessionId, session2Id);

    // Verify all 4 retake transcripts
    for (let i = 0; i < 4; i++) {
      assert.strictEqual(
        retakeBody.report.perQuestionBreakdown[i].transcript,
        retakeAnswers[i].transcript,
        `Retake Question ${i + 1} must match new answers`
      );
    }

    // Verify GET endpoint for the retake session
    const getRetake = await fetch(`${baseUrl}/api/sessions/${session2Id}/report`);
    assert.strictEqual(getRetake.status, 200);
    const getRetakeBody = await getRetake.json();
    assert.strictEqual(getRetakeBody.sessionId, session2Id);

    for (let i = 0; i < 4; i++) {
      assert.strictEqual(
        getRetakeBody.perQuestionBreakdown[i].transcript,
        retakeAnswers[i].transcript,
        `Retake Question ${i + 1} must be persisted under new session ID`
      );
    }
  });

  it("should return 404 for an unknown session ID without falling back to stale data", async () => {
    const unknownId = "ses_non_existent_" + Date.now();
    const res = await fetch(`${baseUrl}/api/sessions/${unknownId}/report`);
    assert.strictEqual(res.status, 404);
    const body = await res.json();
    assert.strictEqual(body.success, false);
    assert.strictEqual(body.error, "NotFound");
  });
});
