"""
Underwriting & Dynamic Pricing Engine
Actuarial pure premium formula with risk-tier loading factors.

Formula:
    Premium = (Frequency * Severity) / (1 - Target_Loss_Ratio - Expense_Loading)
"""

_RISK_MULTIPLIERS = {
    "Low": 1.0,
    "Medium": 1.5,
    "High": 2.5,
}

_BASE_FREQUENCY = 0.15       # Expected claims per year (base)
_BASE_SEVERITY = 50_000.0    # Average claim cost (KES)
_TARGET_LOSS_RATIO = 0.65    # 65% actuarial target
_EXPENSE_LOADING = 0.15      # 15% operational overhead


def calculate_premium(
    risk_tier: str,
    risk_score: float,
    base_frequency: float = _BASE_FREQUENCY,
    base_severity: float = _BASE_SEVERITY,
    target_loss_ratio: float = _TARGET_LOSS_RATIO,
    expense_loading: float = _EXPENSE_LOADING,
) -> dict:
    """
    Calculate risk-adjusted insurance premium.

    Args:
        risk_tier: Low | Medium | High
        risk_score: 0.0 – 1.0 from clinical model
        base_frequency: expected claims per year
        base_severity: average claim cost in KES
        target_loss_ratio: actuarial target loss ratio (default 0.65)
        expense_loading: expense loading factor (default 0.15)

    Returns:
        annual_premium, monthly_premium, pure_premium, risk_multiplier, breakdown
    """
    multiplier = _RISK_MULTIPLIERS.get(risk_tier, 1.0)

    # Risk-score fine-tuning on top of tier multiplier
    score_adjustment = 1.0 + (risk_score * 0.3)

    adjusted_frequency = base_frequency * multiplier * score_adjustment
    adjusted_severity = base_severity * multiplier

    pure_premium = adjusted_frequency * adjusted_severity
    denominator = 1.0 - target_loss_ratio - expense_loading

    if denominator <= 0:
        raise ValueError("target_loss_ratio + expense_loading must be < 1.0")

    annual_premium = pure_premium / denominator
    monthly_premium = annual_premium / 12

    return {
        "annual_premium": round(annual_premium, 2),
        "monthly_premium": round(monthly_premium, 2),
        "pure_premium": round(pure_premium, 2),
        "risk_multiplier": round(multiplier * score_adjustment, 4),
        "loading_factors": {
            "target_loss_ratio": target_loss_ratio,
            "expense_loading": expense_loading,
            "combined_loading": round(1.0 - denominator, 4),
        },
        "breakdown": {
            "adjusted_frequency": round(adjusted_frequency, 6),
            "adjusted_severity": round(adjusted_severity, 2),
            "base_frequency": base_frequency,
            "base_severity": base_severity,
            "risk_tier": risk_tier,
            "risk_score": risk_score,
        },
    }
