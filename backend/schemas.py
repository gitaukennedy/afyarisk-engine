"""
AfyaRisk 2.0 — Pydantic Request/Response Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ─── Health Risk & Underwriting ──────────────────────────────────────────────

class HealthRiskRequest(BaseModel):
    glucose: float = Field(..., ge=60, le=300, description="Blood glucose mg/dL")
    bmi: float = Field(..., ge=10, le=60, description="Body Mass Index kg/m²")
    age: int = Field(..., ge=18, le=100, description="Patient age in years")
    blood_pressure: float = Field(..., ge=40, le=200, description="Diastolic blood pressure mmHg")
    insulin: float = Field(..., ge=0, le=900, description="Serum insulin μU/mL")


class HealthRiskResponse(BaseModel):
    risk_tier: str
    risk_score: float
    survival_probability: float
    health_degradation_3yr: float
    confidence: float
    annual_premium: float
    monthly_premium: float
    pure_premium: float
    risk_multiplier: float
    loading_factors: Dict[str, float]


# ─── Policy Pricing ───────────────────────────────────────────────────────────

class PricingRequest(BaseModel):
    risk_tier: str = Field(..., description="Low | Medium | High")
    risk_score: float = Field(..., ge=0.0, le=1.0)
    base_frequency: Optional[float] = Field(None, ge=0.0, description="Override base claim frequency")
    base_severity: Optional[float] = Field(None, ge=0.0, description="Override base severity (KES)")
    target_loss_ratio: Optional[float] = Field(None, ge=0.0, le=0.99)
    expense_loading: Optional[float] = Field(None, ge=0.0, le=0.99)


class PricingResponse(BaseModel):
    annual_premium: float
    monthly_premium: float
    pure_premium: float
    risk_multiplier: float
    loading_factors: Dict[str, float]
    breakdown: Dict[str, Any]


# ─── Fraud Detection ──────────────────────────────────────────────────────────

class FraudRequest(BaseModel):
    claim_amount: float = Field(..., ge=0, description="Total claim amount (KES)")
    claim_frequency: int = Field(..., ge=0, description="Claims in last 90 days")
    provider_id: int = Field(..., ge=1, description="Healthcare provider numeric ID")
    diagnosis_code: int = Field(..., ge=1, description="ICD-10 numeric code mapping")
    patient_age: int = Field(..., ge=18, le=100)
    days_since_policy: int = Field(..., ge=0, description="Days since policy inception")


class FraudResponse(BaseModel):
    fraud_score: float
    fraud_percentage: float
    is_flagged: bool
    flags: List[str]
    recommendation: str


# ─── IBNR Reserving ───────────────────────────────────────────────────────────

class IBNRRequest(BaseModel):
    triangle: Optional[List[List[float]]] = Field(
        None,
        description="Claims development triangle (n x n). Leave null to use sample data."
    )


class IBNRResponse(BaseModel):
    development_factors: List[float]
    projected_ultimates: List[float]
    ibnr_by_year: List[float]
    total_ibnr: float
    triangle_completed: List[List[Optional[float]]]


# ─── Policy RAG ───────────────────────────────────────────────────────────────

class PolicyQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Natural language policy question")
    top_k: Optional[int] = Field(3, ge=1, le=10)


class MatchedClause(BaseModel):
    clause: str
    source: str
    similarity_score: float


class PolicyQueryResponse(BaseModel):
    query: str
    matched_clauses: List[MatchedClause]
    top_match: str
