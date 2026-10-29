# IMAIRA+ Project

IMAIRA+ is an accent-agnostic technical mock interview platform.
The project is organized into clean full-stack modules with dedicated **frontend** and **backend** layers.

---

## 📁 Project Architecture

```
IMAIRA+/
├── frontend/                      # Client-side web application
│   ├── index.html                 # Production landing page
│   ├── css/
│   │   └── style.css              # Custom styling, animations & typography
│   ├── js/
│   │   ├── tailwind-config.js     # Tailwind CSS theme extension
│   │   ├── typewriter.js          # Dynamic headline typewriter animation
│   │   └── main.js                # Interaction controller & smooth scrolling
│   ├── components/                # Modular section partials
│   │   ├── header.html            # Navigation bar
│   │   ├── hero.html              # Hero section with Rory telemetry card
│   │   ├── architecture.html      # 3-Layer architecture (Fairness Kernel)
│   │   ├── domains.html           # Technical domains bento grid
│   │   ├── benchmarks.html        # Neutrality statistics & region table
│   │   ├── cta-banner.html        # Pre-footer CTA banner
│   │   └── footer.html            # Multi-column footer & ethics links
│   └── assets/
│       └── images/
│           └── screen.png         # Reference design preview
│
└── backend/                       # Node.js / Express API service
    ├── server.js                  # Main server entry point
    ├── package.json               # Dependencies and npm scripts
    ├── .env.example               # Environment variables template
    ├── README.md                  # Backend setup & API documentation
    ├── routes/
    │   └── api.js                 # API route definitions
    └── controllers/
        └── interviewController.js # Session, domain, and benchmark logic
```

---

## 🚀 Running the Project

### 1. Frontend
You can open `frontend/index.html` directly in any web browser, or serve it with:
```bash
npx serve frontend
# or
python -m http.server 8000 --directory frontend
```

### 2. Backend
To run the backend API service:
```bash
cd backend
npm install
npm start
# or for auto-reloading:
npm run dev
```
The backend API will run on `http://localhost:5000` with the health check available at `http://localhost:5000/api/health`.
