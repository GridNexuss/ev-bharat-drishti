"""Shared Pydantic schemas for candidate charging hub locations and MCLP optimisation."""

from typing import Literal

from pydantic import BaseModel, Field


class CandidateSite(BaseModel):
    """Represents a candidate EV charging hub location in Pune District."""

    candidate_id: str = Field(..., min_length=3, description="Unique candidate ID, e.g., CAND_001")
    candidate_name: str = Field(..., min_length=2, description="Human-readable location name")
    zone_id: str = Field(..., description="Pilot analysis zone ID, e.g., ZONE_01")
    site_type: Literal[
        "toll_plaza",
        "bus_depot",
        "it_park",
        "industrial_midc",
        "fuel_outlet",
        "mall_commercial",
        "park_and_ride",
        "substation_yard",
    ]
    latitude: float = Field(..., ge=17.5, le=19.5, description="WGS84 latitude within Pune region")
    longitude: float = Field(..., ge=73.0, le=75.2, description="WGS84 longitude within Pune region")
    capex_inr: float = Field(..., gt=0, description="Estimated capital setup cost in INR")
    capacity_kw: float = Field(..., gt=0, description="Proposed total charger capacity in kW")
    charger_count: int = Field(..., ge=1, description="Number of charging points at the hub")
    data_status: Literal["observed", "estimated", "synthetic_demo"] = Field(
        default="synthetic_demo",
        description="Distinguishes verified field sites from demo/estimated assumptions",
    )
    cost_basis: str = Field(
        ...,
        description="Explicit basis for capex_inr (e.g., assumption_pm_edrive_benchmark)",
    )
    grid_feasibility: Literal["verified", "unknown"] = Field(
        default="unknown",
        description="Missing MSEDCL feeder evidence must remain 'unknown'",
    )


class CandidateSiteCollection(BaseModel):
    """Container for a versioned list of candidate sites."""

    dataset_version: str
    pilot_geography: str = "Pune District, Maharashtra"
    crs: str = "EPSG:4326"
    candidates: list[CandidateSite]


class ZoneWeight(BaseModel):
    """Priority weight (e.g., GAI score or energy deficit) for a Pune pilot zone."""

    zone_id: str
    zone_name: str
    priority_weight: float = Field(..., ge=0, description="Zone priority weight from GAI/demand")


class MCLPResult(BaseModel):
    """Deterministic output from the SciPy/HiGHS budget-constrained MCLP solver."""

    solver_status: Literal["optimal", "infeasible", "suboptimal", "error"]
    budget_inr: float
    total_cost_inr: float
    remaining_budget_inr: float
    objective_value: float
    total_possible_weight: float
    coverage_percentage: float
    selected_candidate_ids: list[str]
    selected_candidates: list[CandidateSite]
    covered_zone_ids: list[str]
    model_note: str = (
        "Deterministic operations-research optimisation (SciPy HiGHS MILP), "
        "not a trained machine-learning model."
    )