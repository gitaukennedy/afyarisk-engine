"""
AfyaRisk 2.0 — FastAPI Backend
Actuarial Health, Fraud & Loss Reserving Engine
"""
import sys
from pathlib import Path

# Add project root (afyarisk-engine) to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now your existing imports will work cleanly:
from schemas import HealthAssessmentInput, HealthAssessmentOutput # or relative import
from engine.clinical_ml import predict_risk
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import (
    HealthRiskRequest, HealthRiskResponse,
    PricingRequest, PricingResponse,
    FraudRequest, FraudResponse,
    IBNRRequest, IBNRResponse,
    PolicyQueryRequest, PolicyQueryResponse,
)
from engine.clinical_ml import predict_risk
from engine.underwriting import calculate_premium
from engine.fraud import detect_fraud
from engine.reserving import calculate_ibnr, SAMPLE_TRIANGLE
from engine.rag_policy import query_policy

app = FastAPI(
    title="AfyaRisk 2.0",
    description="Enterprise Insurtech & Actuarial AI Engine — Clinical Risk, Fraud Detection, IBNR Reserving, Policy RAG",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "AfyaRisk 2.0", "version": "2.0.0"}


@app.post("/api/v1/assess-health-risk", response_model=HealthRiskResponse, tags=["Clinical Risk"])
def assess_health_risk(payload: HealthRiskRequest):
    """
    Full clinical risk assessment + actuarial premium pricing.
    Combines Random Forest risk classification with dynamic premium calculation.
    """
    try:
        clinical = predict_risk(
            glucose=payload.glucose,
            bmi=payload.bmi,
            age=payload.age,
            blood_pressure=payload.blood_pressure,
            insulin=payload.insulin,
        )
        pricing = calculate_premium(
            risk_tier=clinical["risk_tier"],
            risk_score=clinical["risk_score"],
        )
        return HealthRiskResponse(
            risk_tier=clinical["risk_tier"],
            risk_score=clinical["risk_score"],
            survival_probability=clinical["survival_probability"],
            health_degradation_3yr=clinical["health_degradation_3yr"],
            confidence=clinical["confidence"],
            annual_premium=pricing["annual_premium"],
            monthly_premium=pricing["monthly_premium"],
            pure_premium=pricing["pure_premium"],
            risk_multiplier=pricing["risk_multiplier"],
            loading_factors=pricing["loading_factors"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/price-policy", response_model=PricingResponse, tags=["Underwriting"])
def price_policy(payload: PricingRequest):
    """
    Standalone actuarial premium calculation with optional parameter overrides.
    Uses: Premium = (Frequency × Severity) / (1 - Loss Ratio - Expense Loading)
    """
    try:
        kwargs = {"risk_tier": payload.risk_tier, "risk_score": payload.risk_score}
        if payload.base_frequency is not None:
            kwargs["base_frequency"] = payload.base_frequency
        if payload.base_severity is not None:
            kwargs["base_severity"] = payload.base_severity
        if payload.target_loss_ratio is not None:
            kwargs["target_loss_ratio"] = payload.target_loss_ratio
        if payload.expense_loading is not None:
            kwargs["expense_loading"] = payload.expense_loading
        result = calculate_premium(**kwargs)
        return PricingResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/detect-fraud", response_model=FraudResponse, tags=["Fraud Detection"])
def detect_fraud_endpoint(payload: FraudRequest):
    """
    Isolation Forest fraud anomaly detection on claim features.
    Returns fraud score 0–100%, triggered flags, and APPROVE/REVIEW/REJECT recommendation.
    """
    try:
        result = detect_fraud(
            claim_amount=payload.claim_amount,
            claim_frequency=payload.claim_frequency,
            provider_id=payload.provider_id,
            diagnosis_code=payload.diagnosis_code,
            patient_age=payload.patient_age,
            days_since_policy=payload.days_since_policy,
        )
        return FraudResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/calculate-ibnr", response_model=IBNRResponse, tags=["Actuarial Reserving"])
def calculate_ibnr_endpoint(payload: IBNRRequest):
    """
    Chain-Ladder IBNR reserve calculation from a claims development triangle.
    If no triangle is provided, uses the built-in sample triangle.
    """
    try:
        triangle = payload.triangle if payload.triangle else SAMPLE_TRIANGLE
        result = calculate_ibnr(triangle)
        return IBNRResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query-policy", response_model=PolicyQueryResponse, tags=["Policy RAG"])
def query_policy_endpoint(payload: PolicyQueryRequest):
    """
    FAISS semantic vector search over health policy documents.
    Returns top matched policy clauses with similarity scores.
    """
    try:
        result = query_policy(query=payload.query, top_k=payload.top_k or 3)
        return PolicyQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
