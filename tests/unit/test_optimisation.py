"""Unit tests for candidate site schemas and SciPy/HiGHS MCLP optimisation."""

import json
from pathlib import Path

import pytest

from services.analytics.optimisation.mclp import solve_mclp
from services.analytics.optimisation.schemas import (
    CandidateSite,
    CandidateSiteCollection,
    ZoneWeight,
)


def _sample_zones() -> list[ZoneWeight]:
    return [
        ZoneWeight(zone_id="ZONE_01", zone_name="PMC Core", priority_weight=80.0),
        ZoneWeight(zone_id="ZONE_02", zone_name="PCMC Core", priority_weight=75.0),
        ZoneWeight(zone_id="ZONE_03", zone_name="Hinjawadi IT Park", priority_weight=95.0),
    ]


def _sample_candidates() -> list[CandidateSite]:
    return [
        CandidateSite(
            candidate_id="CAND_001",
            candidate_name="Swargate Hub",
            zone_id="ZONE_01",
            site_type="bus_depot",
            latitude=18.5018,
            longitude=73.8636,
            capex_inr=6_000_000,
            capacity_kw=240,
            charger_count=4,
            cost_basis="assumption_test",
        ),
        CandidateSite(
            candidate_id="CAND_002",
            candidate_name="Nigdi Hub",
            zone_id="ZONE_02",
            site_type="bus_depot",
            latitude=18.6515,
            longitude=73.7706,
            capex_inr=6_000_000,
            capacity_kw=240,
            charger_count=4,
            cost_basis="assumption_test",
        ),
        CandidateSite(
            candidate_id="CAND_003",
            candidate_name="Hinjawadi Hub",
            zone_id="ZONE_03",
            site_type="it_park",
            latitude=18.5913,
            longitude=73.7389,
            capex_inr=7_500_000,
            capacity_kw=300,
            charger_count=5,
            cost_basis="assumption_test",
        ),
    ]


def test_sample_candidate_file_validates() -> None:
    sample_path = Path("data/candidates/pune_candidate_sites_sample.json")
    raw = json.loads(sample_path.read_text(encoding="utf-8"))
    collection = CandidateSiteCollection.model_validate(raw)
    assert len(collection.candidates) == 10
    assert all(c.data_status == "synthetic_demo" for c in collection.candidates)


def test_mclp_selects_highest_weight_within_budget() -> None:
    zones = _sample_zones()
    candidates = _sample_candidates()
    # CAND_003 covers both ZONE_02 and ZONE_03 (weight = 75 + 95 = 170)
    coverage = [
        [1, 0, 0],  # ZONE_01 covered by CAND_001
        [0, 1, 1],  # ZONE_02 covered by CAND_002 and CAND_003
        [0, 0, 1],  # ZONE_03 covered by CAND_003
    ]

    result = solve_mclp(zones, candidates, coverage, budget_inr=8_000_000)

    assert result.solver_status == "optimal"
    assert result.selected_candidate_ids == ["CAND_003"]
    assert result.total_cost_inr == 7_500_000
    assert result.objective_value == 170.0
    assert set(result.covered_zone_ids) == {"ZONE_02", "ZONE_03"}


def test_mclp_zero_budget_selects_none() -> None:
    result = solve_mclp(
        _sample_zones(),
        _sample_candidates(),
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        budget_inr=0,
    )
    assert result.solver_status == "optimal"
    assert result.selected_candidate_ids == []
    assert result.total_cost_inr == 0.0
    assert result.objective_value == 0.0


def test_mclp_invalid_matrix_shape_raises() -> None:
    with pytest.raises(ValueError, match="coverage_matrix shape"):
        solve_mclp(
            _sample_zones(),
            _sample_candidates(),
            [[1, 0]],  # Wrong shape
            budget_inr=10_000_000,
        )