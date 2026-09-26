# AfyaRisk 2.0

**Enterprise Insurtech & Actuarial AI Platform**

AfyaRisk 2.0 is a fully functional prototype that unifies five previously siloed insurance workflows — clinical risk scoring, dynamic policy pricing, fraud detection, actuarial loss reserving, and RAG-driven policy querying — into a single real-time API platform with a professional web dashboard.

> Built with IBM Bob as an agentic SDLC assistant across architecture, backend, and frontend.

---

## Live Demo

| Service | URL |
|---|---|
| Frontend Dashboard | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Interactive API Docs | http://localhost:8000/docs |

---

## Features

| Tab | Engine | What it does |
|---|---|---|
| **Health Risk** | Random Forest Classifier | Scores patient biomarkers → Low / Medium / High risk tier + 3yr survival probability + actuarial premium |
| **Policy Pricing** | Actuarial Pure Premium | Calculates risk-adjusted premiums using `(Frequency × Severity) / (1 − Loss Ratio − Expense Loading)` |
| **Fraud Detection** | Isolation Forest | Scores claims 0–100% fraud probability, triggers rule-based flags, returns APPROVE / REVIEW / REJECT |
| **IBNR Reserving** | Chain-Ladder | Computes Incurred But Not Reported reserves from historical claims development triangles |
| **Policy RAG** | FAISS + Sentence Transformers | Semantic search over 15 indexed policy clauses using `all-MiniLM-L6-v2` embeddings |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1 — Install Python dependencies

```bash
pip install fastapi "uvicorn[standard]" scikit-learn xgboost lightgbm pandas numpy scipy pydantic "sentence-transformers" faiss-cpu
```

Or from file:
```bash
pip install -r requirements.txt
```

### 2 — Start the backend

From the project root:
```bash
uvicorn backend.main:app --reload --port 8000
```

You will see in the terminal:
```
AfyaRisk startup: preloading RAG index...
RAG: loading sentence-transformer model...
RAG: index ready — 15 vectors, dim=384
```

The RAG model loads in the background at startup so the first Policy query is instant.

### 3 — Start the frontend

In a separate terminal:
```bash
cd frontend
npm install      # first time only
npm run dev
```

Open **http://localhost:3000**

---

## Project Structure

```
afyarisk-engine/
├── backend/
│   ├── main.py              # FastAPI app + lifespan startup
│   ├── schemas.py           # Pydantic v2 request/response models
│   └── engine/
│       ├── clinical_ml.py   # Random Forest health risk classifier
│       ├── underwriting.py  # Actuarial pure premium calculator
│       ├── fraud.py         # Isolation Forest fraud detector
│       ├── reserving.py     # Chain-Ladder IBNR engine
│       └── rag_policy.py    # FAISS semantic policy search
├── frontend/
│   └── app/
│       ├── page.tsx         # Full 5-tab dashboard (React + Tailwind)
│       ├── layout.tsx       # Root layout
│       └── globals.css      # Theme (light professional, forest green)
├── docs/
│   └── SPEC.md              # Full technical architecture specification
├── requirements.txt         # Python dependencies
└── README.md
```

---

## API Reference

**Base URL:** `http://localhost:8000/api/v1`

### `POST /assess-health-risk`
Full clinical assessment + premium calculation.
```json
{
  "glucose": 140,
  "bmi": 31.2,
  "age": 52,
  "blood_pressure": 88,
  "insulin": 120
}
```

### `POST /price-policy`
Standalone actuarial premium calculation.
```json
{
  "risk_tier": "High",
  "risk_score": 0.78
}
```

### `POST /detect-fraud`
Isolation Forest claim fraud scoring.
```json
{
  "claim_amount": 95000,
  "claim_frequency": 7,
  "provider_id": 580,
  "diagnosis_code": 460,
  "patient_age": 22,
  "days_since_policy": 12
}
```

### `POST /calculate-ibnr`
Chain-Ladder IBNR reserve calculation.
```json
{
  "triangle": [
    [1000, 1500, 1800, 1900],
    [1200, 1750, 2100, 0],
    [1400, 2000, 0, 0],
    [1600, 0, 0, 0]
  ]
}
```
Leave `triangle` null to use the built-in sample triangle.

### `POST /query-policy`
Semantic policy document search.
```json
{
  "query": "What is the waiting period for maternity cover?",
  "top_k": 3
}
```

### `GET /health`
Service health check.

---

## Technology Stack

### Backend
| Component | Technology |
|---|---|
| API Framework | FastAPI ≥ 0.104 |
| Server | Uvicorn (ASGI) |
| ML — Risk | scikit-learn RandomForestClassifier |
| ML — Fraud | scikit-learn IsolationForest |
| Actuarial | Pure Premium + Chain-Ladder (NumPy) |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Vector Store | FAISS (IndexFlatIP, cosine similarity) |
| Schema Validation | Pydantic v2 |

### Frontend
| Component | Technology |
|---|---|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Theme | Light professional, forest green `#0d6e4e` |

---

## Notes

- All ML models are trained on **synthetic data at server startup** — no external datasets required.
- The FAISS index is **built in-memory** and pre-warmed at startup via a background thread.
- This is a **hackathon prototype** — not certified actuarial advice.
- For production: add JWT authentication, persist the FAISS index to disk, and connect to real claims data.

---

*Built with [IBM Bob](https://www.ibm.com/products/bob) — agentic AI software engineering assistant.*
