from __future__ import annotations

import math
from typing import Any


def _name_similarity(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.0
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    return round(len(tokens_a & tokens_b) / len(tokens_a | tokens_b), 3)


def find_duplicate_candidates(
    records: list[dict[str, Any]],
    max_distance_m: float = 50.0,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    valid_records = [
        r
        for r in records
        if r.get("x_32643") is not None
        and r.get("y_32643") is not None
        and r.get("coord_status") != "invalid"
    ]

    for i in range(len(valid_records)):
        for j in range(i + 1, len(valid_records)):
            r1 = valid_records[i]
            r2 = valid_records[j]
            dx = float(r1["x_32643"]) - float(r2["x_32643"])
            dy = float(r1["y_32643"]) - float(r2["y_32643"])
            dist_m = round(math.hypot(dx, dy), 2)

            if dist_m <= max_distance_m:
                sim = _name_similarity(
                    r1.get("station_name_key") or r1.get("station_name"),
                    r2.get("station_name_key") or r2.get("station_name"),
                )
                candidates.append(
                    {
                        "record_id_a": r1.get("source_record_id"),
                        "record_id_b": r2.get("source_record_id"),
                        "source_a": r1.get("source_name"),
                        "source_b": r2.get("source_name"),
                        "distance_m": dist_m,
                        "name_jaccard_similarity": sim,
                        "match_status": "candidate_duplicate",
                    }
                )

    return candidates
