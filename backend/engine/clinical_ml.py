"""
Clinical Risk Prediction Engine
Random Forest Classifier on health biomarkers.
Outputs: Low / Medium / High risk tier + survival probability.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


def _build_synthetic_training_data():
    """Generate synthetic biomarker training data — all 3 risk classes guaranteed."""
    rng = np.random.RandomState(42)
    n = 1200

    # Spread distributions wide enough to produce Low, Medium AND High examples
    glucose = rng.normal(130, 60, n).clip(60, 300)
    bmi = rng.normal(30, 10, n).clip(15, 60)
    age = rng.normal(50, 20, n).clip(18, 90)
    blood_pressure = rng.normal(85, 20, n).clip(40, 200)
    insulin = rng.normal(100, 80, n).clip(0, 900)

    # Synthetic risk label: weighted clinical heuristic
    risk_score_raw = (
        (glucose - 70) / 230 * 0.35
        + (bmi - 18) / 42 * 0.25
        + (age - 18) / 72 * 0.20
        + (blood_pressure - 40) / 160 * 0.10
        + (insulin / 900) * 0.10
    )

    labels = np.where(risk_score_raw < 0.35, 0, np.where(risk_score_raw < 0.65, 1, 2))

    # Guarantee at least 50 samples of each class so the model learns all 3 tiers
    for cls, lo, hi in [(0, 0.0, 0.34), (1, 0.35, 0.64), (2, 0.65, 1.0)]:
        needed = max(0, 50 - int((labels == cls).sum()))
        if needed:
            extra_scores = rng.uniform(lo, hi, needed)
            extra_glucose = 70 + extra_scores * 230
            extra_bmi = np.full(needed, 25.0)
            extra_age = np.full(needed, 45.0)
            extra_bp = np.full(needed, 80.0)
            extra_insulin = np.full(needed, 50.0)
            glucose = np.append(glucose, extra_glucose)
            bmi = np.append(bmi, extra_bmi)
            age = np.append(age, extra_age)
            blood_pressure = np.append(blood_pressure, extra_bp)
            insulin = np.append(insulin, extra_insulin)
            labels = np.append(labels, np.full(needed, cls))

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
    predicted_class = int(_model.classes_[int(np.argmax(proba))])
    tier = _TIER_MAP.get(predicted_class, "Medium")

    # Build full 3-class probability array safely regardless of classes learned
    classes = list(_model.classes_)
    p = [float(proba[classes.index(c)]) if c in classes else 0.0 for c in [0, 1, 2]]

    # Composite risk score (weighted toward high-risk probability)
    risk_score = float(p[1] * 0.4 + p[2] * 1.0)
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
