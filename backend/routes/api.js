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

// Technical domains endpoints
router.get("/domains", interviewController.getDomains);

// Mock session endpoints
router.post("/sessions/start", interviewController.startSession);

// Benchmarks and neutrality metrics endpoint
router.get("/benchmarks", interviewController.getFairnessMetrics);

module.exports = router;
