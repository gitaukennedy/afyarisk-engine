# AfyaRisk 2.0 — Actuarial Health, Fraud & Loss Reserving Engine

AfyaRisk 2.0 is an enterprise insurtech engine that unifies clinical risk scoring, dynamic policy pricing, fraud detection, actuarial loss reserving (IBNR), and RAG-driven policy querying into a single platform.

## Architecture Flow
`Next.js Frontend` <--> `FastAPI Backend` <--> `Scikit-Learn / XGBoost / Lifelines / FAISS Engines`

## Core Modules
- **Clinical Risk:** Random Forest Classifier predicting biomarker health risk tiers.
- **Underwriting:** Risk-adjusted pure premium calculation using expected loss ratios.
- **Fraud Detection:** Isolation Forest anomaly detection flagging billing irregularities.
- **Actuarial Reserving:** Chain-Ladder development factor algorithm computing IBNR reserves.
- **Policy RAG:** Vector similarity search querying policy rules and underwriting guidelines.

## IBM Bob Integration
Built leveraging IBM Bob for spec-driven development, modular backend scaffolding, and full-repo context awareness.