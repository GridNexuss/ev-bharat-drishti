import json
from pathlib import Path

from services.etl.cleaning.station_normalizer import normalize_station_records
from services.etl.deduplication.duplicate_finder import find_duplicate_candidates
from services.etl.validation.coordinate_validator import validate_station_records


def test_sample_pipeline_end_to_end() -> None:
    sample_path = Path("data/sample/pune_stations_sample.json")
    raw = json.loads(sample_path.read_text(encoding="utf-8-sig"))

    normalized = normalize_station_records(raw)
    assert len(normalized) == 5

    by_id_norm = {r["source_record_id"]: r for r in normalized}
    assert by_id_norm["OSM-NODE-1001"]["connectors"] == ["CCS2", "TYPE2"]
    assert by_id_norm["EVY-PUNE-2001"]["reported_status"] == "operational"
    assert by_id_norm["EVY-PUNE-2002"]["reported_status"] == "unknown"

    validated = validate_station_records(normalized)
    by_id_val = {r["source_record_id"]: r for r in validated}
    assert by_id_val["OSM-NODE-1001"]["coord_status"] == "valid_pune"
    assert "swapped_lat_lon_suspected" in by_id_val["EVY-PUNE-2002"]["coord_flags"]
    assert "outside_pune_district_bbox" in by_id_val["OSM-NODE-1003"]["coord_flags"]

    candidates = find_duplicate_candidates(validated, max_distance_m=50.0)
    assert len(candidates) == 1
    assert {candidates[0]["record_id_a"], candidates[0]["record_id_b"]} == {
        "OSM-NODE-1001",
        "EVY-PUNE-2001",
    }
    assert candidates[0]["distance_m"] < 30.0
