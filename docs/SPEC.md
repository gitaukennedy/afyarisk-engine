# AfyaRisk 2.0 — Technical Architecture Specification

**Version:** 2.0.0  
**Classification:** Enterprise Insurtech & Actuarial AI Platform  
**Author:** AfyaRisk Engineering Team  
**Date:** 2026  
**Status:** Hackathon Prototype — Fully Functional

---

## 1. Executive Summary

AfyaRisk 2.0 is an integrated, AI-powered actuarial engine that unifies five previously siloed insurtech workflows into a single real-time API platform with a professional web dashboard.

| Workflow | Technology | Output |
|---|---|---|
| Clinical Risk Classification | Random Forest Classifier | Low / Medium / High risk tier |
| Dynamic Policy Pricing | Actuarial Pure Premium Formula | Risk-adjusted premium (KES) |
| Fraud Detection | Isolation Forest Anomaly Detection | Fraud Score 0–100% + flag list |
| Loss Reserving (IBNR) | Deterministic Chain-Ladder | IBNR reserve requirement |
| Policy RAG Pipeline | FAISS + Sentence Transformers | Matched policy clauses |

---

## 2. Problem Statement

Insurtech platforms struggle with disjointed workflows:
- Health risk classification relies on clinical indicators processed in isolation
- Loss reserving relies on historical claims triangles in spreadsheets
- Fraud detection relies on isolated rule sets with no ML feedback
- Dynamic policy pricing operates in silos disconnected from real-time risk data

**Results:** Mispriced risk pools, elevated loss ratios, fraudulent claim leakage, and delayed actuarial reserve adjustments.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AfyaRisk 2.0 Platform                    │
├─────────────────┬───────────────────────────────────────────┤
│  Next.js 15     │         FastAPI Backend (Python)          │
│  Frontend       │                                           │
│  Dashboard      │  ┌──────────────────────────────────┐    │
│                 │  │         Engine Layer              │    │
│  Tab 1: Health  │  │  ┌────────────────────────────┐  │    │
│  Tab 2: Pricing │  │  │  clinical_ml.py             │  │    │
│  Tab 3: Fraud   │  │  │  (Random Forest Classifier) │  │    │
│  Tab 4: IBNR    │  │  ├────────────────────────────┤  │    │
│  Tab 5: Policy  │  │  │  underwriting.py            │  │    │
│                 │  │  │  (Actuarial Pure Premium)   │  │    │
│   HTTP/REST     │  │  ├────────────────────────────┤  │    │
│   API calls     │  │  │  fraud.py                  │  │    │
│   localhost:    │  │  │  (Isolation Forest)         │  │    │
│   8000          │  │  ├────────────────────────────┤  │    │
│                 │  │  │  reserving.py               │  │    │
│                 │  │  │  (Chain-Ladder IBNR)        │  │    │
│                 │  │  ├────────────────────────────┤  │    │
│                 │  │  │  rag_policy.py              │  │    │
│                 │  │  │  (FAISS Vector Search)      │  │    │
│                 │  │  └────────────────────────────┘  │    │
│                 │  └──────────────────────────────────┘    │
└─────────────────┴───────────────────────────────────────────┘
```

---

## 4. Module Specifications

### 4.1 Clinical Risk Prediction (`engine/clinical_ml.py`)

**Algorithm:** Random Forest Classifier (scikit-learn)  
**Training Data:** Synthetic health biomarker dataset (1,200 samples, guaranteed all 3 classes)

**Input Features:**

| Feature | Type | Range | Clinical Significance |
|---|---|---|---|
| glucose | float | 60–300 mg/dL | Primary diabetes indicator |
| bmi | float | 10–60 kg/m² | Obesity and metabolic risk |
| age | int | 18–100 years | Age-related comorbidity risk |
| blood_pressure | float | 40–200 mmHg | Cardiovascular risk factor |
| insulin | float | 0–900 μU/mL | Insulin resistance marker |

**Output Schema:**
```json
{
  "risk_tier": "Low | Medium | High",
  "risk_score": 0.0,
  "survival_probability": 0.0,
  "health_degradation_3yr": 0.0,
  "confidence": 0.0
}
```

**Risk Tier Thresholds:**
- Low: score < 0.35
- Medium: 0.35 ≤ score < 0.65
- High: score ≥ 0.65

**Model Parameters:**
```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=8,
    min_samples_split=5,
    random_state=42
)
```

**Implementation Notes:**
- Training data uses wider distributions than original to ensure all 3 classes are represented
- Minimum 50 samples guaranteed per class via synthetic augmentation
- `predict_risk` safely maps output probabilities via `_model.classes_` — never assumes fixed class ordering

---

### 4.2 Underwriting & Dynamic Pricing (`engine/underwriting.py`)

**Formula:**
```
Premium = (Frequency × Severity) / (1 - Target_Loss_Ratio - Expense_Loading_Factor)
```

**Parameter Definitions:**

| Parameter | Default | Description |
|---|---|---|
| base_frequency | 0.15 | Expected claim events per year |
| base_severity | KES 50,000 | Average claim cost |
| target_loss_ratio | 0.65 | Actuarial target (65%) |
| expense_loading | 0.15 | Operational overhead (15%) |
| risk_multiplier | tier-based | Low=1.0, Medium=1.5, High=2.5 |

**Risk Multiplier Schedule:**
```
Low Risk    → multiplier = 1.0  (base rate)
Medium Risk → multiplier = 1.5  (+50% loading)
High Risk   → multiplier = 2.5  (+150% loading)
```

**Output Schema:**
```json
{
  "annual_premium": 0.0,
  "monthly_premium": 0.0,
  "pure_premium": 0.0,
  "risk_multiplier": 0.0,
  "loading_factors": {},
  "breakdown": {}
}
```

---

### 4.3 Fraud Detection Engine (`engine/fraud.py`)

**Algorithm:** Isolation Forest (scikit-learn)  
**Training Data:** 2,000 synthetic legitimate claims

**Input Features:**

| Feature | Description |
|---|---|
| claim_amount | Total monetary value of claim (KES) |
| claim_frequency | Number of claims in rolling 90-day window |
| provider_id | Numeric provider identifier |
| diagnosis_code | ICD-10 code numeric mapping |
| patient_age | Policyholder age |
| days_since_policy | Days since policy inception |

**Fraud Score Derivation:**
```
raw_score = isolation_forest.decision_function(features)
fraud_score = 1 - (raw_score - min) / (max - min)  # normalized 0–1
```

**Flag Triggers:**
- `HIGH_CLAIM_AMOUNT`: claim > 3σ above mean
- `RAPID_RESUBMISSION`: frequency > 5 in 90 days
- `PROVIDER_MISMATCH`: provider outside normal range (110–550)
- `DIAGNOSIS_AGE_MISMATCH`: high code + young patient
- `EARLY_POLICY_LARGE_CLAIM`: large claim within 30 days of inception

**Decision Rules:**
```
fraud_percentage ≥ 75% OR ≥ 3 flags  → REJECT
fraud_percentage ≥ 50% OR ≥ 2 flags  → REVIEW
otherwise                             → APPROVE
```

---

### 4.4 Loss Reserving Engine (`engine/reserving.py`)

**Algorithm:** Deterministic Chain-Ladder Method

**Chain-Ladder Steps:**
1. Compute age-to-age development factors: `f_k = Σ C(i,k+1) / Σ C(i,k)`
2. Project ultimate losses for each accident year
3. IBNR = Ultimate Loss − Latest Diagonal (reported losses)
4. Total IBNR = Σ IBNR across all open accident years

**Output Schema:**
```json
{
  "development_factors": [],
  "projected_ultimates": [],
  "ibnr_by_year": [],
  "total_ibnr": 0.0,
  "triangle_completed": []
}
```

---

### 4.5 Medical Policy RAG Pipeline (`engine/rag_policy.py`)

**Architecture:** Retrieval-Augmented Generation (RAG)  
**Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`  
**Vector Store:** FAISS (IndexFlatIP — cosine similarity via L2-normalised inner product)  
**Indexed Documents:** 15 policy clauses (waiting periods, exclusions, ICD-10 codes, fraud, IBNR, etc.)

**Pipeline Flow:**
```
Server Startup → Background Thread → Encode 15 documents → FAISS Index (ready in ~15s)
                                                                   ↓
User Query → Query Embedding → Similarity Search (top-k) → Matched Clauses
```

**Performance:**
- Index is preloaded at server startup via `preload()` background thread
- Thread-safe via `threading.Lock()` — safe under concurrent requests
- First query after restart is instant (index pre-warmed)
- `_ready` flag prevents double-build

**Output Schema:**
```json
{
  "query": "string",
  "matched_clauses": [
    {
      "clause": "string",
      "source": "string",
      "similarity_score": 0.0
    }
  ],
  "top_match": "string"
}
```

---

## 5. API Endpoint Specification

**Base URL:** `http://localhost:8000/api/v1`

| Endpoint | Method | Engine | Description |
|---|---|---|---|
| `/assess-health-risk` | POST | clinical_ml + underwriting | Full health assessment + premium |
| `/price-policy` | POST | underwriting | Standalone premium calculation |
| `/detect-fraud` | POST | fraud | Claim fraud scoring |
| `/calculate-ibnr` | POST | reserving | IBNR reserve computation |
| `/query-policy` | POST | rag_policy | Policy clause retrieval |
| `/health` | GET | — | Service health check |

---

## 6. Technology Stack

### Backend
| Component | Technology | Version |
|---|---|---|
| API Framework | FastAPI | ≥ 0.104 |
| Server | Uvicorn (ASGI) | ≥ 0.24 |
| ML Framework | scikit-learn | ≥ 1.4 |
| Data Processing | pandas + numpy | latest |
| Embeddings | sentence-transformers | ≥ 2.2 |
| Vector Store | faiss-cpu | ≥ 1.7 |
| Schema Validation | Pydantic v2 | ≥ 2.5 |

### Frontend
| Component | Technology |
|---|---|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Theme | Light professional — forest green `#0d6e4e`, warm off-white `#f8f7f4` |

---

## 7. Data Flow

```
Patient Biomarkers → Clinical ML → Risk Tier + Survival Probability
                                         ↓
Risk Tier + Score → Underwriting → Annual / Monthly Premium
                                         ↓
Claim Submission → Fraud Detection → Score + Flags + Recommendation
                                         ↓
Historical Triangle → Chain-Ladder → IBNR Reserve by Accident Year
                                         ↓
Policy Query → FAISS RAG → Top-K Matched Policy Clauses
```

---

## 8. Server Startup Sequence

```
uvicorn backend.main:app
    ↓
FastAPI lifespan() event fires
    ↓
preload_rag() → background thread starts
    ↓
clinical_ml module loads → RandomForest trains on synthetic data (~2s)
fraud module loads → IsolationForest trains on synthetic data (~1s)
    ↓                           (in parallel, background)
RAG thread: loads sentence-transformer → encodes 15 docs → FAISS index built (~15s)
    ↓
Server ready on port 8000
All engines warm — zero cold-start latency on first request
```

---

## 9. Security & Compliance

- All endpoints validate input via Pydantic v2 schemas with field-level constraints
- CORS configured for frontend origin (`localhost:3000`)
- No PII stored in vector index (anonymised policy text only)
- IBNR outputs clearly marked as estimates, not certified actuarial opinions
- Fraud flags include explainable rule-based triggers alongside ML score

---

## 10. Hackathon Scope & Production Path

| Feature | Prototype | Production |
|---|---|---|
| Training data | Synthetic (startup) | Real historical claims dataset |
| FAISS index | In-memory | Persisted `.index` file |
| Authentication | None | JWT / OAuth2 |
| Models | In-memory | Serialised with joblib / MLflow |
| Deployment | localhost | Docker → Railway / Render (backend), Vercel (frontend) |
| Monitoring | uvicorn logs | Prometheus + Grafana |
