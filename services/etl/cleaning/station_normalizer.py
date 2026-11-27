from __future__ import annotations

import re
from typing import Any

_CONNECTOR_MAP = {
    "ccs2": "CCS2",
    "ccs-2": "CCS2",
    "ccs 2": "CCS2",
    "type2": "TYPE2",
    "type-2": "TYPE2",
    "type 2": "TYPE2",
    "levdc": "LEVDC",
    "lev-dc": "LEVDC",
    "lev dc": "LEVDC",
    "chademo": "CHADEMO",
}

_STATUS_MAP = {
    "operational": "operational",
    "active": "operational",
    "online": "operational",
    "offline": "offline",
    "inactive": "offline",
    "maintenance": "maintenance",
    "under_maintenance": "maintenance",
}


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text if text else None


def normalize_connector(connector: Any) -> str | None:
    cleaned = clean_text(connector)
    if cleaned is None:
        return None
    key = cleaned.lower()
    return _CONNECTOR_MAP.get(key, cleaned.upper())


def normalize_status(status: Any) -> str:
    cleaned = clean_text(status)
    if cleaned is None:
        return "unknown"
    return _STATUS_MAP.get(cleaned.lower(), cleaned.lower())


def normalize_station_record(record: dict[str, Any]) -> dict[str, Any]:
    station_name = clean_text(record.get("station_name"))
    operator = clean_text(record.get("operator"))

    raw_connectors = record.get("connectors") or []
    normalized_connectors = sorted(
        {
            norm
            for item in raw_connectors
            if (norm := normalize_connector(item)) is not None
        }
    )

    normalized_key = re.sub(r"[^a-z0-9]+", " ", (station_name or "").lower()).strip()

    return {
        "source_record_id": clean_text(record.get("source_record_id")),
        "source_name": clean_text(record.get("source_name")),
        "source_url": clean_text(record.get("source_url")),
        "access_classification": clean_text(record.get("access_classification")),
        "fetched_at": clean_text(record.get("fetched_at")),
        "station_name": station_name,
        "station_name_key": normalized_key or None,
        "operator": operator.title() if operator and operator.islower() else operator,
        "latitude": record.get("latitude"),
        "longitude": record.get("longitude"),
        "connectors": normalized_connectors,
        "reported_status": normalize_status(record.get("reported_status")),
    }


def normalize_station_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_station_record(rec) for rec in records]
