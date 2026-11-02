# AI Resume Analyzer & Job Matcher

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12%20|%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-33%20Passed%20(83%25%20Coverage)-success.svg)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full-stack web application that parses resumes in **PDF** and **DOCX** formats, compares them against target job descriptions using **explainable weighted scoring and TF-IDF cosine similarity**, extracts structured candidate data, generates grounded resume improvement suggestions, tracks evaluation history, and exports executive PDF reports.

Designed to operate with **zero paid API dependencies** out-of-the-box via deterministic NLP, while offering optional pluggable LLM support (OpenAI, Gemini) when configured.

---

## Key Features

- **Multi-Format Parsing**: Extracts structured text and metadata from PDF (PyMuPDF) and Word documents (python-docx) with scanned image detection and defensive validation.
- **Explainable Scoring Engine**: Computes transparent weighted scores across Skills (50%), Semantic Text Overlap / TF-IDF (25%), Experience (15%), and Education (10%), with dynamic reweighting when education is omitted in the job description.
- **Skill Taxonomy & Evidence Quotes**: Detects canonical skills, distinguishes between required vs. preferred competencies, and extracts exact sentences from the resume as proof.
- **Grounded Resume Enhancements**: Formats bullet points into Google's XYZ formula (`Accomplished [X] as measured by [Y], by doing [Z]`) with honest placeholders, preserving candidate context and proper noun capitalization.
- **Executive PDF Export**: Generates downloadable evaluation summaries using ReportLab.
- **Security & Multi-Tenancy**: Argon2 password hashing with complexity rules, stateless JWT authentication, in-memory sliding-window rate limiting, and strict row-level user data isolation.

---

## Tech Stack

- **Backend**: Python 3.12+ / 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, SQLite (dev) / PostgreSQL (prod), Uvicorn.
- **NLP & Parsing**: PyMuPDF, python-docx, scikit-learn (TF-IDF & cosine similarity), ReportLab.
- **Security**: PyJWT, pwdlib with Argon2.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts, Axios.
- **Testing**: pytest, pytest-asyncio, pytest-cov (33 automated tests, 83% coverage).

---

## Quick Start Guide

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`

### 2. Frontend Setup

In a separate terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

- Web Application: `http://localhost:5173`

---

## Running Automated Tests

Run backend unit and security tests:

```bash
cd backend
.\venv\Scripts\python.exe -m pytest -v --cov=app
```

Run frontend type check and production build:

```bash
cd frontend
npm run build
```

---

## Environment Configuration

Configure the `.env` file in the `backend/` directory:

| Variable | Default | Purpose |
|---|---|---|
| `ENVIRONMENT` | `development` | `development`, `testing`, or `production` |
| `SECRET_KEY` | *(dev default)* | JWT secret (min 32 chars required in production) |
| `DATABASE_URL` | `sqlite:///./resume_matcher.db` | Database connection string |
| `RATE_LIMIT_ENABLED` | `true` | Enables in-memory sliding-window rate limiting |
| `LLM_PROVIDER` | `none` | Optional LLM provider (`none`, `gemini`, `openai`) |
| `LLM_API_KEY` | `null` | API key if using an optional external LLM |

---

## Project Structure

```
ai-resume-analyzer/
├── backend/
│   ├── alembic/              # Database migration versions
│   ├── app/
│   │   ├── models/           # SQLAlchemy database entities (User, Resume, Analysis)
│   │   ├── routers/          # FastAPI route controllers (auth, resumes, analyses, dashboard)
│   │   ├── schemas/          # Pydantic request and response schemas
│   │   ├── security/         # Argon2 password hashing and JWT token handlers
│   │   ├── services/         # Parsers, skill matchers, scoring engine, AI recommendations
│   │   ├── utils/            # Rate limiting, file validation, custom exceptions
│   │   ├── config.py         # Application settings and environment validation
│   │   ├── database.py       # SQLAlchemy engine and session factory
│   │   └── main.py           # FastAPI entrypoint, middleware, and lifespan
│   ├── tests/                # Automated pytest suite (auth, parser, scoring, rate limiting)
│   ├── Dockerfile            # Backend container configuration
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # UI widgets (ScoreGauge, FileUploader, SkillsBadgeList, Navbar)
│   │   ├── contexts/         # Authentication and Theme React contexts
│   │   ├── pages/            # Views (Landing, Login, Register, Dashboard, Analyze, Results, History)
│   │   ├── services/         # Axios API service clients
│   │   ├── types/            # TypeScript data definitions
│   │   ├── App.tsx           # Router and page composition
│   │   └── main.tsx          # React application entrypoint
│   ├── Dockerfile            # Multi-stage Nginx container configuration
│   └── package.json          # Node dependencies and build scripts
├── docker-compose.yml        # Multi-container orchestration (FastAPI + PostgreSQL + Nginx)
├── LICENSE                   # MIT License
└── README.md                 # Project documentation
```

---

## Disclaimer

This product provides heuristic algorithmic estimates based on keyword matching, TF-IDF content similarity, and structured extraction. It does not guarantee interview callbacks or employment selection outcomes.

---

## License

This project is licensed under the [MIT License](LICENSE).
