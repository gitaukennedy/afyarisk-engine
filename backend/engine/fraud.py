"""
Fraud Detection Engine
Isolation Forest anomaly detector on claims features.
Returns Fraud Score 0–100% and a list of triggered flags.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def _build_synthetic_claims_data():
    """Generate synthetic legitimate claims training data."""
    rng = np.random.RandomState(42)
    n = 2000

    claim_amount = rng.exponential(15000, n).clip(500, 200_000)
    claim_frequency = rng.poisson(1.2, n).clip(0, 10).astype(float)
    provider_id = rng.randint(100, 600, n).astype(float)
    diagnosis_code = rng.randint(1, 500, n).astype(float)
    patient_age = rng.normal(40, 15, n).clip(18, 90)
    days_since_policy = rng.exponential(365, n).clip(1, 3650)

    return np.column_stack([
        claim_amount, claim_frequency, provider_id,
        diagnosis_code, patient_age, days_since_policy
    ])


_X_train = _build_synthetic_claims_data()
_scaler = StandardScaler().fit(_X_train)
_X_scaled = _scaler.transform(_X_train)

_model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42,
)
_model.fit(_X_scaled)

# Calibrate score range from training data
_train_scores = _model.decision_function(_X_scaled)
_score_min = float(_train_scores.min())
_score_max = float(_train_scores.max())

# Statistical thresholds from training data
_MEAN_AMOUNT = float(_X_train[:, 0].mean())
_STD_AMOUNT = float(_X_train[:, 0].std())


def detect_fraud(
    claim_amount: float,
    claim_frequency: int,
    provider_id: int,
    diagnosis_code: int,
    patient_age: int,
    days_since_policy: int,
) -> dict:
    """
    Assess fraud risk for a submitted claim.

    Returns:
        fraud_score: 0.0 – 1.0
        fraud_percentage: 0.0 – 100.0
        is_flagged: bool
        flags: list of triggered flag names
        recommendation: APPROVE | REVIEW | REJECT
    """
    features = np.array([[
        float(claim_amount),
        float(claim_frequency),
        float(provider_id),
        float(diagnosis_code),
        float(patient_age),
        float(days_since_policy),
    ]])
    features_scaled = _scaler.transform(features)

    raw_score = float(_model.decision_function(features_scaled)[0])

    # Normalize to 0–1 (higher = more fraudulent)
    score_range = _score_max - _score_min
    fraud_score = 1.0 - (raw_score - _score_min) / score_range if score_range > 0 else 0.5
    fraud_score = float(np.clip(fraud_score, 0.0, 1.0))
    fraud_percentage = round(fraud_score * 100, 2)

    # Rule-based flag triggers
    flags = []
    if claim_amount > _MEAN_AMOUNT + 3 * _STD_AMOUNT:
        flags.append("HIGH_CLAIM_AMOUNT")
    if claim_frequency > 5:
        flags.append("RAPID_RESUBMISSION")
    if provider_id > 550 or provider_id < 110:
        flags.append("PROVIDER_MISMATCH")
    if diagnosis_code > 450 and patient_age < 25:
        flags.append("DIAGNOSIS_AGE_MISMATCH")
    if days_since_policy < 30 and claim_amount > 30_000:
        flags.append("EARLY_POLICY_LARGE_CLAIM")

    is_flagged = fraud_score > 0.6 or len(flags) >= 2

    if fraud_percentage >= 75 or len(flags) >= 3:
        recommendation = "REJECT"
    elif fraud_percentage >= 50 or len(flags) >= 2:
        recommendation = "REVIEW"
    else:
        recommendation = "APPROVE"

    return {
        "fraud_score": round(fraud_score, 4),
        "fraud_percentage": fraud_percentage,
        "is_flagged": is_flagged,
        "flags": flags,
        "recommendation": recommendation,
    }
