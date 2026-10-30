/**
 * IMAIRA+ Backend Server Entrypoint
 * Express server providing APIs for sessions, neutrality telemetry, and domain catalogs.
 */
require("dotenv").config();
const express = require("express");
const cors = require("cors");
const apiRoutes = require("./routes/api");
const authRoutes = require("./routes/auth");
const speechRoutes = require("./routes/speech");

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Mount API routes under /api
app.use("/api/auth", authRoutes);
app.use("/api/speech", speechRoutes);
app.use("/api", apiRoutes);

// Root greeting
app.get("/", (req, res) => {
  res.json({
    message: "Welcome to IMAIRA+ Mock Interview API Service",
    documentation: "/api/health"
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: "Not Found",
    message: `Cannot ${req.method} ${req.originalUrl}`
  });
});

// Global error handler
app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json({
      error: "Bad Request",
      message: "Malformed JSON payload"
    });
  }
  console.error("Internal Server Error:", err.stack);
  res.status(err.status || 500).json({
    error: "Internal Server Error",
    message: err.message || "Something went wrong on the server"
  });
});

// Start listening
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`IMAIRA+ Backend Server running on port ${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/api/health`);
  });
}

module.exports = app;
