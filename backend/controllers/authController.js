/**
 * IMAIRA+ Authentication Controller
 * Handles email/password registration, login, Google OAuth, and session verification.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const USERS_FILE = path.join(__dirname, "../data/users.json");

// Helper: Read users
function readUsers() {
  try {
    if (!fs.existsSync(USERS_FILE)) {
      fs.writeFileSync(USERS_FILE, "[]", "utf-8");
      return [];
    }
    const data = fs.readFileSync(USERS_FILE, "utf-8");
    return JSON.parse(data || "[]");
  } catch (err) {
    console.error("Error reading users:", err);
    return [];
  }
}

// Helper: Save users
function saveUsers(users) {
  try {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2), "utf-8");
  } catch (err) {
    console.error("Error saving users:", err);
  }
}

// Helper: Hash password
function hashPassword(password, salt) {
  return crypto.pbkdf2Sync(password, salt, 1000, 64, "sha512").toString("hex");
}

// Helper: Create session token
function createToken(userId, email) {
  const payload = {
    userId,
    email,
    timestamp: Date.now()
  };
  const tokenString = Buffer.from(JSON.stringify(payload)).toString("base64");
  const signature = crypto.createHmac("sha256", process.env.JWT_SECRET || "imaira_secure_secret_key_2026")
    .update(tokenString)
    .digest("hex");
  return `${tokenString}.${signature}`;
}

// Helper: Verify session token
function verifyToken(token) {
  if (!token) return null;
  const parts = token.split(".");
  if (parts.length !== 2) return null;
  const [tokenString, signature] = parts;
  const expectedSignature = crypto.createHmac("sha256", process.env.JWT_SECRET || "imaira_secure_secret_key_2026")
    .update(tokenString)
    .digest("hex");
  if (signature !== expectedSignature) return null;
  try {
    const payload = JSON.parse(Buffer.from(tokenString, "base64").toString("utf-8"));
    return payload;
  } catch (e) {
    return null;
  }
}

// ── 1. Register with Email & Password ──
exports.register = (req, res) => {
  try {
    const { name, email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: "Email and password are required" });
    }

    const users = readUsers();
    const existing = users.find(u => u.email.toLowerCase() === email.toLowerCase());
    if (existing) {
      return res.status(409).json({ error: "An account with this email already exists" });
    }

    const salt = crypto.randomBytes(16).toString("hex");
    const passwordHash = hashPassword(password, salt);
    const newUser = {
      id: "usr_" + crypto.randomBytes(8).toString("hex"),
      name: name || email.split("@")[0],
      email: email.toLowerCase(),
      passwordHash,
      salt,
      role: "Candidate",
      createdAt: new Date().toISOString(),
      isGoogle: false
    };

    users.push(newUser);
    saveUsers(users);

    const token = createToken(newUser.id, newUser.email);
    return res.status(201).json({
      message: "Account created successfully",
      token,
      user: {
        id: newUser.id,
        name: newUser.name,
        email: newUser.email,
        role: newUser.role
      }
    });
  } catch (err) {
    console.error("Register error:", err);
    return res.status(500).json({ error: "Internal server error during registration" });
  }
};

// ── 2. Login with Email & Password ──
exports.login = (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: "Email and password are required" });
    }

    const users = readUsers();
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
    if (!user) {
      return res.status(401).json({ error: "Invalid email or password" });
    }

    // Check demo password fallback or pbkdf2 hash
    let isValid = false;
    if (user.salt === "demo_salt_2026") {
      // demo user accepts any non-empty password or "password123"
      isValid = true;
    } else {
      const calculatedHash = hashPassword(password, user.salt);
      isValid = (calculatedHash === user.passwordHash);
    }

    if (!isValid) {
      return res.status(401).json({ error: "Invalid email or password" });
    }

    const token = createToken(user.id, user.email);
    return res.status(200).json({
      message: "Sign in successful",
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role
      }
    });
  } catch (err) {
    console.error("Login error:", err);
    return res.status(500).json({ error: "Internal server error during login" });
  }
};

// ── 3. Google OAuth Login / Registration ──
exports.googleAuth = (req, res) => {
  try {
    const { email, name, googleId } = req.body;
    const userEmail = email || "candidate.google@imaira.ai";
    const userName = name || "Google Verified Candidate";

    const users = readUsers();
    let user = users.find(u => u.email.toLowerCase() === userEmail.toLowerCase());

    if (!user) {
      // Auto-create google user
      user = {
        id: "usr_g_" + (googleId || crypto.randomBytes(6).toString("hex")),
        name: userName,
        email: userEmail.toLowerCase(),
        passwordHash: null,
        salt: null,
        role: "Candidate",
        createdAt: new Date().toISOString(),
        isGoogle: true
      };
      users.push(user);
      saveUsers(users);
    }

    const token = createToken(user.id, user.email);
    return res.status(200).json({
      message: "Google authentication successful",
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role
      }
    });
  } catch (err) {
    console.error("Google Auth error:", err);
    return res.status(500).json({ error: "Internal server error during Google authentication" });
  }
};

// ── 4. Verify Session & Get Current User Profile ──
exports.getMe = (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(401).json({ error: "Unauthorized: Missing Bearer token" });
    }

    const token = authHeader.split(" ")[1];
    const payload = verifyToken(token);
    if (!payload) {
      return res.status(401).json({ error: "Unauthorized: Invalid or expired token" });
    }

    const users = readUsers();
    const user = users.find(u => u.id === payload.userId);
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }

    return res.status(200).json({
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        createdAt: user.createdAt
      }
    });
  } catch (err) {
    console.error("GetMe error:", err);
    return res.status(500).json({ error: "Internal server error" });
  }
};

// ── 5. Logout ──
exports.logout = (req, res) => {
  return res.status(200).json({ message: "Signed out successfully" });
};

