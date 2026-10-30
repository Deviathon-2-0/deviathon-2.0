/**
 * IMAIRA+ Speech Routes
 * 
 * Endpoints for audio transcription, speech synthesis, and provider metadata.
 */
const express = require("express");
const router = express.Router();
const speechController = require("../controllers/speechController");
const { upload } = require("../middleware/upload");

// Middleware to catch multer-specific errors (e.g. file size exceeded, invalid MIME)
const handleUpload = (req, res, next) => {
  upload.single("audio")(req, res, (err) => {
    if (err) {
      if (err.code === "LIMIT_FILE_SIZE") {
        return res.status(400).json({
          error: "File Too Large",
          message: "Uploaded audio exceeds the 25MB file size limit."
        });
      }
      return res.status(400).json({
        error: "Upload Error",
        message: err.message || "Failed to process audio upload."
      });
    }
    next();
  });
};

// POST /api/speech/transcribe - Transcribe uploaded audio
router.post("/transcribe", handleUpload, speechController.transcribe);

// POST /api/speech/synthesize - Synthesize text to speech
router.post("/synthesize", speechController.synthesize);

// GET /api/speech/providers - Get info on active speech providers & glossary
router.get("/providers", speechController.getProviders);

module.exports = router;
