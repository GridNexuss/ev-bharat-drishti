"""Budget-constrained Maximum Covering Location Problem (MCLP) solver using SciPy HiGHS."""

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from services.analytics.optimisation.schemas import (
    CandidateSite,
    MCLPResult,
    ZoneWeight,
)


def solve_mclp(
    zones: list[ZoneWeight],
    candidates: list[CandidateSite],
    coverage_matrix: list[list[int]],
    budget_inr: float,
) -> MCLPResult:
    """Solve the budget-constrained MCLP using SciPy's HiGHS MILP solver.

    Args:
        zones: List of zones with priority weights w_i.
        candidates: List of candidate sites with capital cost c_j.
        coverage_matrix: Binary matrix A of shape (num_zones, num_candidates),
            where A[i][j] = 1 if candidate j covers zone i within threshold time.
        budget_inr: Maximum available capital budget B in INR.

    Returns:
        MCLPResult with selected candidates, covered zones, cost, and solver status.
    """
    num_zones = len(zones)
    num_candidates = len(candidates)

    if num_zones == 0 or num_candidates == 0:
        raise ValueError("Zones and candidates lists must not be empty.")
    if budget_inr < 0:
        raise ValueError("Budget must be non-negative.")

    A = np.asarray(coverage_matrix, dtype=float)
    if A.shape != (num_zones, num_candidates):
        raise ValueError(
            f"coverage_matrix shape {A.shape} does not match "
            f"({num_zones} zones, {num_candidates} candidates)."
        )

    weights = np.array([z.priority_weight for z in zones], dtype=float)
    costs = np.array([c.capex_inr for c in candidates], dtype=float)
    total_possible_weight = float(np.sum(weights))

    # Decision variables:
    # First num_candidates variables are x_j (1 if candidate j is selected, else 0)
    # Next num_zones variables are y_i (1 if zone i is covered, else 0)
    # scipy.optimize.milp MINIMIZES c^T x, so we negate zone weights to maximize coverage.
    c_obj = np.concatenate([np.zeros(num_candidates), -weights])

    # All variables are binary (0 or 1)
    integrality = np.ones(num_candidates + num_zones)
    bounds = Bounds(lb=np.zeros(num_candidates + num_zones), ub=np.ones(num_candidates + num_zones))

    # Constraint 1 (Budget): sum_j (cost_j * x_j) <= budget_inr
    budget_row = np.concatenate([costs, np.zeros(num_zones)])

    # Constraint 2 (Coverage): y_i - sum_j (A[i, j] * x_j) <= 0  for each zone i
    # Ensures a zone can only be marked covered (y_i = 1) if at least one covering hub is built.
    coverage_rows = np.hstack([-A, np.eye(num_zones)])

    constraint_matrix = np.vstack([budget_row, coverage_rows])
    lower_bounds = np.full(1 + num_zones, -np.inf)
    upper_bounds = np.concatenate([[budget_inr], np.zeros(num_zones)])

    constraints = LinearConstraint(constraint_matrix, lb=lower_bounds, ub=upper_bounds)

    res = milp(
        c=c_obj,
        integrality=integrality,
        bounds=bounds,
        constraints=constraints,
    )

    if not res.success or res.x is None:
        return MCLPResult(
            solver_status="infeasible" if res.status == 2 else "error",
            budget_inr=budget_inr,
            total_cost_inr=0.0,
            remaining_budget_inr=budget_inr,
            objective_value=0.0,
            total_possible_weight=total_possible_weight,
            coverage_percentage=0.0,
            selected_candidate_ids=[],
            selected_candidates=[],
            covered_zone_ids=[],
        )

    x_sol = np.round(res.x[:num_candidates]).astype(int)
    y_sol = np.round(res.x[num_candidates:]).astype(int)

    selected_candidates = [candidates[j] for j in range(num_candidates) if x_sol[j] == 1]
    selected_ids = [c.candidate_id for c in selected_candidates]
    covered_zone_ids = [zones[i].zone_id for i in range(num_zones) if y_sol[i] == 1]

    total_cost = float(sum(c.capex_inr for c in selected_candidates))
    objective_value = float(sum(zones[i].priority_weight for i in range(num_zones) if y_sol[i] == 1))
    coverage_pct = (
        round((objective_value / total_possible_weight) * 100.0, 2)
        if total_possible_weight > 0
        else 0.0
    )

    return MCLPResult(
        solver_status="optimal" if res.status == 0 else "suboptimal",
        budget_inr=budget_inr,
        total_cost_inr=total_cost,
        remaining_budget_inr=budget_inr - total_cost,
        objective_value=objective_value,
        total_possible_weight=total_possible_weight,
        coverage_percentage=coverage_pct,
        selected_candidate_ids=selected_ids,
        selected_candidates=selected_candidates,
        covered_zone_ids=covered_zone_ids,
    )