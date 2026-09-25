"""
Loss Reserving Engine — Deterministic Chain-Ladder Method
Computes IBNR reserves from a historical claims development triangle.
"""

import numpy as np
from typing import List


def calculate_ibnr(triangle: List[List[float]]) -> dict:
    """
    Apply Chain-Ladder method to a claims development triangle.

    Args:
        triangle: n x n matrix where triangle[i][j] is cumulative paid
                  losses for accident year i at development period j.
                  Use 0 or None for unknown (future) cells.

    Returns:
        development_factors: age-to-age link ratios
        projected_ultimates: projected ultimate loss per accident year
        ibnr_by_year: IBNR reserve per accident year
        total_ibnr: total reserve requirement
        triangle_completed: completed/filled development triangle
    """
    tri = np.array(triangle, dtype=float)
    n = tri.shape[0]

    # Replace 0s in upper triangle with NaN for cleaner factor computation
    for i in range(n):
        for j in range(n):
            if j > n - 1 - i:
                tri[i][j] = np.nan

    # Step 1: Compute age-to-age development factors
    development_factors = []
    for k in range(n - 1):
        numerator = 0.0
        denominator = 0.0
        for i in range(n - k - 1):
            if not np.isnan(tri[i][k]) and not np.isnan(tri[i][k + 1]):
                numerator += tri[i][k + 1]
                denominator += tri[i][k]
        factor = numerator / denominator if denominator > 0 else 1.0
        development_factors.append(round(factor, 6))

    # Step 2: Complete the triangle
    completed = tri.copy()
    for i in range(1, n):
        last_known_col = n - i - 1
        for j in range(last_known_col + 1, n):
            completed[i][j] = completed[i][j - 1] * development_factors[j - 1]

    # Step 3: Project ultimate losses
    projected_ultimates = [round(float(completed[i][n - 1]), 2) for i in range(n)]

    # Latest diagonal = most recent reported losses per accident year
    latest_diagonal = []
    for i in range(n):
        last_col = n - 1 - i
        latest_diagonal.append(float(tri[i][last_col]) if not np.isnan(tri[i][last_col]) else 0.0)

    # Step 4: IBNR = Ultimate - Latest reported
    ibnr_by_year = [
        round(projected_ultimates[i] - latest_diagonal[i], 2)
        for i in range(n)
    ]
    total_ibnr = round(sum(ibnr_by_year), 2)

    # Convert completed triangle back to list, replacing NaN with computed values
    completed_list = [
        [round(float(v), 2) if not np.isnan(v) else None for v in row]
        for row in completed
    ]

    return {
        "development_factors": development_factors,
        "projected_ultimates": projected_ultimates,
        "ibnr_by_year": ibnr_by_year,
        "total_ibnr": total_ibnr,
        "triangle_completed": completed_list,
    }


# Default sample triangle for demo/testing
SAMPLE_TRIANGLE = [
    [1000, 1500, 1800, 1900],
    [1200, 1750, 2100,    0],
    [1400, 2000,    0,    0],
    [1600,    0,    0,    0],
]
