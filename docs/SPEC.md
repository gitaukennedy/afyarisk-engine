# AfyaRisk 2.0 — Technical Architecture Specification

**Version:** 2.0.0  
**Classification:** Enterprise Insurtech & Actuarial AI Platform  
**Author:** AfyaRisk Engineering Team  
**Date:** 2025  

---

## 1. Executive Summary

AfyaRisk 2.0 is an integrated, AI-powered actuarial engine that unifies four previously siloed insurtech workflows into a single real-time API platform:

| Workflow | Technology | Output |
|---|---|---|
| Clinical Risk Classification | Random Forest Classifier | Low / Medium / High risk tier |
| Dynamic Policy Pricing | Actuarial Pure Premium Formula | Risk-adjusted premium (KES/USD) |
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
│  Next.js 14     │         FastAPI Backend (Python)          │
│  Frontend       │                                           │
│  Dashboard      │  ┌──────────────────────────────────┐    │
│                 │  │         Engine Layer              │    │
│  Tab 1: Health  │  │  ┌────────────────────────────┐  │    │
│  Tab 2: Fraud   │  │  │  clinical_ml.py             │  │    │
│  Tab 3: IBNR    │  │  │  (Random Forest Classifier) │  │    │
│  Tab 4: Policy  │  │  ├────────────────────────────┤  │    │
│                 │  │  │  underwriting.py            │  │    │
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
**Training Data:** Synthetic health biomarker dataset (Pima Indians Diabetes-inspired)

**Input Features:**

| Feature | Type | Range | Clinical Significance |
|---|---|---|---|
| glucose | float | 0–300 mg/dL | Primary diabetes indicator |
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

---

### 4.2 Underwriting & Dynamic Pricing (`engine/underwriting.py`)

**Formula:**
```
Premium = (Frequency × Severity) / (1 - Target_Loss_Ratio - Expense_Loading_Factor)
```

**Parameter Definitions:**

| Parameter | Default | Description |
|---|---|---|
| base_frequency | risk-adjusted | Expected claim events per year |
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
**Principle:** Anomaly isolation — fraudulent claims are statistically isolated faster than legitimate ones in random partitioning trees.

**Input Features:**

| Feature | Description |
|---|---|
| claim_amount | Total monetary value of claim (KES) |
| claim_frequency | Number of claims in rolling 90-day window |
| provider_id | Numeric provider identifier for variance tracking |
| diagnosis_code | ICD-10 code numeric mapping |
| patient_age | Policyholder age |
| days_since_policy | Days since policy inception |

**Fraud Score Derivation:**
```
raw_score = isolation_forest.decision_function(features)
fraud_score = 1 - (raw_score - min) / (max - min)  # normalized 0–1
fraud_percentage = fraud_score * 100
```

**Flag Triggers:**
- `HIGH_CLAIM_AMOUNT`: claim > 3σ above mean
- `RAPID_RESUBMISSION`: frequency > 5 in 90 days
- `PROVIDER_MISMATCH`: provider variance anomaly
- `DIAGNOSIS_MISMATCH`: code statistically inconsistent with age/claim

**Output Schema:**
```json
{
  "fraud_score": 0.0,
  "fraud_percentage": 0.0,
  "is_flagged": false,
  "flags": [],
  "recommendation": "APPROVE | REVIEW | REJECT"
}
```

---

### 4.4 Loss Reserving Engine (`engine/reserving.py`)

**Algorithm:** Deterministic Chain-Ladder Method  
**Purpose:** Calculate IBNR (Incurred But Not Reported) reserves from historical claims development triangles.

**Input:** Claims development triangle (n×n matrix)
```
        Dev 1   Dev 2   Dev 3   Dev 4
AY 2020  1000    1500    1800    1900
AY 2021  1200    1750    2100      --
AY 2022  1400    2000      --      --
AY 2023  1600      --      --      --
```

**Chain-Ladder Steps:**
1. Compute age-to-age development factors: `f_k = Σ C(i,k+1) / Σ C(i,k)`
2. Project ultimate losses for each accident year
3. IBNR = Ultimate Loss - Latest Diagonal (reported losses)
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
**Vector Store:** FAISS (Facebook AI Similarity Search)

**Pipeline Flow:**
```
Policy Documents → Chunking (512 tokens) → Embeddings → FAISS Index
                                                              ↓
User Query → Query Embedding → Similarity Search (top-k=3) → Matched Clauses
```

**Indexed Document Types:**
- Health policy terms & conditions
- ICD-10 medical code reference tables
- Underwriting eligibility rules
- Exclusion clauses and waiting periods
- Claims processing guidelines

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
| API Framework | FastAPI | ≥0.104 |
| Server | Uvicorn | ≥0.24 |
| ML Framework | scikit-learn | ≥1.3 |
| Boosting | XGBoost + LightGBM | ≥2.0 |
| Data Processing | pandas + numpy | latest |
| Embeddings | sentence-transformers | ≥2.2 |
| Vector Store | faiss-cpu | ≥1.7 |
| Schema Validation | Pydantic v2 | ≥2.0 |

### Frontend
| Component | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS + Dark Mode |
| Charts | Recharts |
| Icons | Lucide React |

---

## 7. Data Flow

```
Patient Biomarkers → Clinical ML → Risk Tier
                                        ↓
Risk Tier + Severity → Underwriting → Premium
                                        ↓
Claim Submission → Fraud Detection → Score + Flags
                                        ↓
Historical Triangle → Chain-Ladder → IBNR Reserve
                                        ↓
Policy Query → RAG Pipeline → Matched Clauses
```

---

## 8. Security & Compliance

- All endpoints validate input via Pydantic v2 schemas
- CORS configured for frontend origin
- No PII stored in vector index (anonymized policy text only)
- Fraud flags are audit-logged with timestamp
- IBNR outputs are clearly marked as estimates, not certified actuarial opinions

---

## 9. Deployment Architecture

```
Frontend (Next.js) → Vercel / Docker
Backend (FastAPI)  → Docker Container / Railway / Render
Vector Index       → Persisted FAISS index file (faiss_policy.index)
Models             → In-memory trained on startup (synthetic data)
```

---

## 10. Hackathon Scope Limitations

- Models are trained on **synthetic data** at startup (no external dataset required)
- FAISS index is **in-memory** (not persisted between restarts in dev mode)
- Chain-Ladder uses **hard-coded sample triangle** as demo input
- No authentication layer in hackathon build (add JWT for production)
- Frontend connects to `localhost:8000` with offline fallback calculations
