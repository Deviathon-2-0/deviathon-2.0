# IMAIRA+
### Mock interviews that hear the answer, not the accent (`IM-103 ADVANCED`)

IMAIRA+ is an accent-tolerant technical mock interview platform built for hackathon track **IM-103**. Standard speech recognition and AI interviewers frequently mishear technical terms spoken with regional or syllable-timed accents (e.g., Indian English) or falsely penalize natural cadence as "robotic." IMAIRA+ solves this with a zero-lag phonetic normalizer and decoupled fairness scoring.

---

## 🛠️ Tech Stack

Keep it simple, reliable, and production-ready:

| Layer | Technologies | Purpose |
|---|---|---|
| **Frontend** | Vanilla JavaScript, Tailwind CSS, Vite | Clean, fast, zero-bloat client interface |
| **Backend** | Python 3.11+, Django 5, Django REST Framework | Core API, session state, and scoring engine |
| **Database** | PostgreSQL | Persistent question bank, company tags, and user sessions |
| **Speech & Phonetics** | Web Speech API, RapidFuzz, Jellyfish (Soundex & Double Metaphone) | Tier 1 instant transcription and Tier 2 sub-5ms phonetic normalization |
| **AI Engine** | Google Gemini 3.4 (`gemini-3.4` / `gemini-3-flash-preview`) | Tier 3 asynchronous accent mining and evaluation synthesis |
| **Code Sandbox** | Multi-language Execution Engine (Python 3.14, C++ GCC 14, Node.js) | Real-time code compilation and automated test case evaluation |

---

## 🎯 What We Promised: Solving IM-103

### 1. The Core Problem
1. **STT Lexicon Drift**: Standard ASR converts technical jargon into everyday conversational words:
   - `"hashmap"` $\to$ `"has aman"` or `"haz a man"`
   - `"tuples"` $\to$ `"two pulse"`
   - `"dijkstra"` $\to$ `"dike stra"`
   - `"asymptotic"` $\to$ `"a symptomatic"`
   - `"O(1)"` $\to$ `"oh one"`
   - `"vector clock"` $\to$ `"wector clock"`
2. **Accent Bias**: Syllable-timed speech patterns (common in Indian English) are falsely penalized by native stress-timed pitch thresholds as "monotone."
3. **Style over Substance**: Evaluators often conflate accent and sentence phrasing with technical competence.

### 2. Our Solution

#### A. 3-Tier Zero-Lag Speech Pipeline
- **Tier 1 (Client-Side, Instant $0\text{ms}$)**: Native browser Web Speech API (`lang: 'en-IN'`, `continuous: true`, `interimResults: true`) renders spoken words on screen with zero network delay.
- **Tier 2 (Server-Side, $<5\text{ms}$ Normalizer)**: [`accent_normalizer.py`](backend/evaluator/accent_normalizer.py) runs an $N$-gram sliding window ($5$-gram to $1$-gram) against our 2,000+ technical glossary using RapidFuzz ($\ge 82\%$) and lazy Double Metaphone / Soundex alignment. It fixes slips like `"haz a man"` $\to$ `"hashmap"` in **$4.19\text{ms}$**.
- **Tier 3 (Async Self-Learning Miner)**: [`async_learner.py`](backend/evaluator/async_learner.py) runs in a background daemon thread calling **Gemini 3.4** to discover new accent slips and persist them to [`dynamic_accent_cache.json`](backend/data/dynamic_accent_cache.json) with **$0\text{ms}$ added latency** to the candidate.

#### B. Decoupled Fairness Scoring
- **Acoustic Calibration**: Baseline vocal pitch ($F_0$) and cadence are calculated during the first 15 seconds (candidate self-intro). Candidates are scored relative to their own natural range, not an arbitrary native accent.
- **Independent Rubric Grading**: Technical depth is scored strictly on concept graph completion (time complexity, data structure choices, trade-offs) with zero deduction for regional pronunciation or colloquial syntax.

#### C. Agreement with Human Standards
- 120 curated interview questions with checklist points derived from human technical interviewer rubrics.

---

## 💻 Core Workspace Features

- **Automatic View Routing**:
  - Advancing to a **Coding question** automatically routes the candidate to the **Editorial View** (code editor, problem statement with clean LaTeX formatting, test cases, and sandbox).
  - Advancing to a **Non-Coding question** (Behavioral, Conceptual, HR, Warm-up) automatically routes the candidate to the **Interviewer View** (full-stage conversational UI with realistic avatar and clean subtitle captions).
- **Manual View Toggle**: Candidate can click the top-bar button (`Editorial (Code)` $\leftrightarrow$ `Interviewer (Stage)`) anytime to switch views manually.
- **Code Draft Persistence**: Code drafted by the candidate persists in memory across questions and view changes—it is never reset or cleared when navigating.
- **Live Compiler Sandbox**: Execute Python, C++, and JavaScript directly in the browser against test cases with instant pass/fail feedback.
- **Silent Interviewer During Coding**: The interviewer avatar stays quiet while the candidate reads and codes, speaking only during conversational questions and follow-ups.

---

## 🚀 Extra Features

- **100 Enterprise Companies Dataset**: Practice role-based or company-specific tracks (Google, AWS, Meta, Apple, Netflix, Uber, Stripe, etc.) mapped to company-tagged LeetCode problems and system design rubrics.
- **Adaptive Cross-Examination**: Interviewer generates dynamic follow-up questions challenging candidate implementation trade-offs and edge cases.
- **Resume Auditing & Roadmaps**: Upload resumes for automated keyword audits and personalized preparation plans.
- **1-Click Judge Access**: Instant guest login on [`auth.html`](frontend/pages/auth.html) for fast hackathon evaluation without sign-up friction.

---

## 🔒 Guardrails & Privacy Compliance

- **Audio Privacy**: Audio is processed in memory; raw candidate audio is deleted immediately after scoring unless the candidate explicitly opts in to save it.
- **Technology**: Powered by efficient open-weight models and approved Google GenAI (**Gemini 3.4**) APIs.
- **Safe Sandboxing**: Code execution runs in isolated sub-process sandboxes with strict execution timeouts (5s) and memory limits.

---

## ⚡ Quickstart

### 1. Database Setup
```sql
CREATE DATABASE imaira_db;
```
Add your credentials in `.env`:
```env
DB_NAME=imaira_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
GEMINI_API_KEY=your_gemini_api_key
```

### 2. Start Backend (Port 8000)
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/core_seed.json
python manage.py loaddata fixtures/catalog_questions.json
python manage.py loaddata fixtures/company_mappings.json
python manage.py runserver 8000
```

### 3. Start Frontend (Port 3000)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser and click **"1-Click Judge Access"**.

### 4. Run Automated Test Suite
```bash
# Test sub-5ms latency and phonetic normalization accuracy
python backend/manage.py test tests.test_accent_normalizer

# Test API endpoints (sandbox, session submission, telemetry)
python backend/manage.py test tests.test_django_api
```

---
<sub>Built for fair, dialect-neutral technical interviews. IMAIRA+ &copy; 2026.</sub>
