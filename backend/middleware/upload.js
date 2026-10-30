/**
 * IMAIRA+ Upload Middleware
 * 
 * Multer-based audio upload handler with file type, size,
 * and format validation. Stores files in OS temp directory
 * for transient processing only.
 */
const multer = require("multer");
const path = require("path");
const os = require("os");
const fs = require("fs");
const { v4: uuidv4 } = require("uuid");

// Temp upload directory — cleaned up after processing
const UPLOAD_DIR = path.join(os.tmpdir(), "imaira_audio_uploads");

// Ensure the temp directory exists
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Allowed MIME types
const ALLOWED_MIME_TYPES = [
  "audio/webm",
  "audio/wav",
  "audio/wave",
  "audio/x-wav",
  "audio/mp3",
  "audio/mpeg",
  "audio/ogg",
  "audio/mp4",
  "audio/x-m4a",
  "audio/m4a"
];

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25 MB

// Multer storage configuration — custom filename with UUID
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, UPLOAD_DIR);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname) || ".webm";
    const safeName = `imaira_${uuidv4()}${ext}`;
    cb(null, safeName);
  }
});

// File filter — reject unsupported formats early
const fileFilter = (req, file, cb) => {
  const mimeType = (file.mimetype || "").toLowerCase();
  if (ALLOWED_MIME_TYPES.includes(mimeType)) {
    cb(null, true);
  } else {
    cb(
      new Error(`Unsupported audio format: ${mimeType}. Accepted: ${ALLOWED_MIME_TYPES.join(", ")}`),
      false
    );
  }
};

// Configured multer instance
const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: MAX_FILE_SIZE,
    files: 1
  }
});

/**
 * Clean up a temporary audio file.
 * Safe to call with null/undefined — silently ignores.
 */
function cleanupTempFile(filePath) {
  if (!filePath) return;
  try {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      console.log(`[Upload] Cleaned up temp file: ${path.basename(filePath)}`);
    }
  } catch (err) {
    console.error(`[Upload] Failed to clean up temp file ${filePath}:`, err.message);
  }
}

/**
 * Get upload directory path (for tests or admin).
 */
function getUploadDir() {
  return UPLOAD_DIR;
}

module.exports = {
  upload,
  cleanupTempFile,
  getUploadDir,
  UPLOAD_DIR,
  ALLOWED_MIME_TYPES,
  MAX_FILE_SIZE
};
