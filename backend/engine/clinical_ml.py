"""
Clinical Risk Prediction Engine
Random Forest Classifier on health biomarkers.
Outputs: Low / Medium / High risk tier + survival probability.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


def _build_synthetic_training_data():
    """Generate synthetic biomarker training data."""
    rng = np.random.RandomState(42)
    n = 1000

    glucose = rng.normal(120, 40, n).clip(60, 300)
    bmi = rng.normal(28, 7, n).clip(15, 60)
    age = rng.normal(45, 15, n).clip(18, 90)
    blood_pressure = rng.normal(80, 15, n).clip(40, 140)
    insulin = rng.normal(80, 60, n).clip(0, 500)

    # Synthetic risk label: weighted clinical heuristic
    risk_score_raw = (
        (glucose - 70) / 230 * 0.35
        + (bmi - 18) / 42 * 0.25
        + (age - 18) / 72 * 0.20
        + (blood_pressure - 40) / 100 * 0.10
        + (insulin / 500) * 0.10
    )

    labels = np.where(risk_score_raw < 0.35, 0, np.where(risk_score_raw < 0.65, 1, 2))

    X = np.column_stack([glucose, bmi, age, blood_pressure, insulin])
    return X, labels


# Train once at module load
_X, _y = _build_synthetic_training_data()
_scaler = StandardScaler().fit(_X)
_X_scaled = _scaler.transform(_X)

_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,
    min_samples_split=5,
    random_state=42,
)
_model.fit(_X_scaled, _y)

_TIER_MAP = {0: "Low", 1: "Medium", 2: "High"}


def predict_risk(glucose: float, bmi: float, age: int, blood_pressure: float, insulin: float) -> dict:
    """
    Predict clinical risk tier and health metrics.

    Returns:
        risk_tier: Low | Medium | High
        risk_score: 0.0 – 1.0
        survival_probability: estimated 3-year survival probability
        health_degradation_3yr: probability of health status decline in 3 years
        confidence: model prediction confidence
    """
    features = np.array([[glucose, bmi, age, blood_pressure, insulin]])
    features_scaled = _scaler.transform(features)

    proba = _model.predict_proba(features_scaled)[0]  # [P_low, P_med, P_high]
    predicted_class = int(np.argmax(proba))
    tier = _TIER_MAP[predicted_class]

    # Composite risk score (weighted toward high-risk probability)
    risk_score = float(proba[1] * 0.4 + proba[2] * 1.0)
    risk_score = min(risk_score, 1.0)

    # Survival probability inversely related to risk
    survival_probability = round(1.0 - (risk_score * 0.45), 4)
    health_degradation_3yr = round(risk_score * 0.60, 4)

    return {
        "risk_tier": tier,
        "risk_score": round(risk_score, 4),
        "survival_probability": survival_probability,
        "health_degradation_3yr": health_degradation_3yr,
        "confidence": round(float(np.max(proba)), 4),
    }
