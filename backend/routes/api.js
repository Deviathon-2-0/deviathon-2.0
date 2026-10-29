/**
 * IMAIRA+ API Routes
 */
const express = require("express");
const router = express.Router();
const interviewController = require("../controllers/interviewController");

// Health check endpoint
router.get("/health", (req, res) => {
  res.status(200).json({
    status: "ok",
    service: "IMAIRA+ Core Engine API",
    timestamp: new Date().toISOString()
  });
});

// Roles API (all 255 roles with categories & levels)
router.get("/roles", interviewController.getRoles);

// Companies API (100 companies with sectors & 10 subroles each)
router.get("/companies", interviewController.getCompanies);
router.get("/companies/:name/subroles", interviewController.getCompanySubroles);

// Questions Engine API
router.post("/interview/questions", interviewController.getQuestions);

// Code Execution / Compiler API
router.post("/compiler/execute", interviewController.executeCode);

// Sessions Management API
router.post("/sessions/start", interviewController.startSession);
router.post("/sessions/:id/submit", interviewController.submitSession);
router.get("/sessions/:id/report", interviewController.getSessionReport);

module.exports = router;
