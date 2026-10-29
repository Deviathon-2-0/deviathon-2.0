# IMAIRA+ Backend Service (Django REST Framework + Gemini 2.5)

Production-grade, headless REST API server for the **IMAIRA+** Accent-Agnostic Mock Interview & Candidate Calibration Platform.

Designed to operate completely standalone without requiring a static UI build or frontend server.

---

## 🛠️ Tech Stack & Architecture
- **Framework**: Django 5.2.x + Django REST Framework 3.17.x
- **Cross-Origin**: `django-cors-headers` (configured for decoupled SPA/Vite, mobile, and CLI clients)
- **AI Core**: Google Gemini 2.5 (`gemini-2.5-flash` / `gemini-2.5-flash-preview-tts` for authentic interviewer accents)
- **Speech Engines**:
  - **TTS**: Server-side PCM-to-WAV generation for 9 authentic interviewer accent profiles (`en-IN`, `en-GB`, `en-US`, `ja-JP`)
  - **STT**: Verbatim transcription with phoneme acoustic normalization & technical glossary validation
- **Sandbox**: Subprocess execution sandbox for Python, JavaScript, Java, C++, and Go
- **Integrity Matrix**: Real-time 3-signal candidate performance & integrity telemetry (eye gaze, posture, pitch variance, saccades, cross-modal lip-sync)
- **Database**: SQLite / PostgreSQL with empty baseline schema ready for production

---

## 🚀 Running the Headless Backend

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables
Create or verify `.env` in the repository root or `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DJANGO_SECRET_KEY=your_secret_key_here
```

### 3. Apply Database Migrations (Schema Only)
Keep the database clean and empty:
```bash
python backend/manage.py migrate
```

### 4. Start the Backend API Server
```bash
# Direct manage.py execution:
python backend/manage.py runserver 0.0.0.0:8000

# Or using the root wrapper:
python manage.py runserver 0.0.0.0:8000

# Or via npm script:
npm run dev:backend
```

The API will be live at `http://localhost:8000/`.

---

## 📡 REST API Reference

All endpoints accept and return pure JSON (`application/json`) with standard HTTP status codes.

### System & Health
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service overview & interactive directory |
| `GET` | `/health` or `/api/health/` | Service health, Gemini connectivity & DB status |
| `GET` | `/api/` | REST collection directory |

### Authentication & Sessions
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register/` | Register candidate account (`email`, `password`, `name`) |
| `POST` | `/api/auth/login/` | Authenticate candidate credentials, returns auth token |
| `POST` | `/api/auth/google/` | Google OAuth token/session registration & login |
| `GET` | `/api/auth/me/` | Fetch authenticated candidate identity & profile |
| `POST` | `/api/auth/logout/` | Invalidate token / sign out |

### Catalogs & Personas
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/roles/` | All 255 curated roles (with `category` and `search` query parameters) |
| `GET` | `/api/companies/` | All 100 enterprise companies (with `sector` and `search` query parameters) |
| `GET` | `/api/companies/<id>/subroles/` | 10 subroles specific to a target enterprise |
| `GET` | `/api/interviewers/` | All 9 evaluators with avatars, bcp47 tags & ethnic accent specs |

### Speech & AI Engines
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/tts/generate/` | Synthesize authentic speech for chosen interviewer (`text`, `interviewer_name`) |
| `POST` | `/api/stt/transcribe/` | Transcribe recorded audio with technical glossary matching |

### Mock Interview Lifecycle & Candidate Matrix
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/questions/` | Generate role & seniority calibrated interview questions |
| `POST` | `/api/sessions/start/` | Create a new interview session and initialize questions |
| `POST` | `/api/sessions/<id>/submit/` | Submit answers for AI rubric scoring across 4 dimensions |
| `GET` | `/api/sessions/<id>/report/` | Retrieve diagnostic scorecard & breakdown |
| `POST` | `/api/sessions/<id>/telemetry/` | Push 3-signal candidate performance & integrity telemetry |

### Code Sandbox & Prep Tools
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/compiler/execute/` | Run candidate code in isolated runtime (`code`, `language`, `stdin`) |
| `POST` | `/api/resume/analyze/` | Parse resume and generate ATS score, strengths, and gap questions |
| `GET` | `/api/assessments/tracks/` | Retrieve assessment quizzes by track |
| `POST` | `/api/assessments/submit/` | Submit and score assessment responses |
| `POST` | `/api/prep-plan/generate/` | Generate customized daily preparation schedule |
| `GET` | `/api/dashboard/summary/` | Aggregate real candidate session statistics and trend metrics |
| `GET/PUT`| `/api/profile/` | Fetch or update candidate user profile |

---

## 🧪 Running the Backend Test Suite
```bash
python backend/manage.py test tests.test_django_api
```
All tests verify endpoint availability, JSON compliance, schema validation, and database operations.
