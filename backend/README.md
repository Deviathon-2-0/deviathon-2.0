# IMAIRA+ Backend Service

Express.js REST API service for the IMAIRA+ accent-agnostic mock interview platform.

---

## 🛠️ Tech Stack
- **Node.js** & **Express**
- **CORS** for secure frontend communications
- **dotenv** for environment variables

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
cd backend
npm install
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run Development Server
```bash
npm start
# or for auto-reload during development:
npm run dev
```

The server will start at `http://localhost:5000`.

---

## 📡 Available Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service status and uptime check |
| `GET` | `/api/domains` | List available technical interview domains |
| `POST` | `/api/sessions/start` | Launch mock interview session with Rory |
| `GET` | `/api/benchmarks` | Neutrality and fairness telemetry statistics |
