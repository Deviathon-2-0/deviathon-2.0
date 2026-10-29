/**
 * IMAIRA+ Authentication Routes
 */
const express = require("express");
const router = express.Router();
const authController = require("../controllers/authController");

// Register with email & password
router.post("/register", authController.register);

// Login with email & password
router.post("/login", authController.login);

// Google OAuth
router.post("/google", authController.googleAuth);

// Get current session user
router.get("/me", authController.getMe);

// Logout
router.post("/logout", authController.logout);

module.exports = router;

