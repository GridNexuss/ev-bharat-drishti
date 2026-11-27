from __future__ import annotations

import math
from typing import Any

PUNE_LAT_MIN = 17.85
PUNE_LAT_MAX = 19.45
PUNE_LON_MIN = 73.30
PUNE_LON_MAX = 75.15


def _to_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(num) or math.isinf(num):
        return None
    return num


def _wgs84_to_utm43n(lat: float, lon: float) -> tuple[float, float]:
    try:
        from pyproj import Transformer

        transformer = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
        easting, northing = transformer.transform(lon, lat)
        return round(float(easting), 3), round(float(northing), 3)
    except Exception:
        a = 6378137.0
        f = 1.0 / 298.257223563
        e_sq = 2 * f - f * f
        ep_sq = e_sq / (1.0 - e_sq)
        k0 = 0.9996

        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        lon0_rad = math.radians(75.0)

        sin_lat = math.sin(lat_rad)
        cos_lat = math.cos(lat_rad)
        tan_lat = math.tan(lat_rad)

        n = a / math.sqrt(1.0 - e_sq * sin_lat * sin_lat)
        t = tan_lat * tan_lat
        c = ep_sq * cos_lat * cos_lat
        big_a = cos_lat * (lon_rad - lon0_rad)

        m = a * (
            (1.0 - e_sq / 4.0 - 3.0 * e_sq * e_sq / 64.0 - 5.0 * (e_sq**3) / 256.0) * lat_rad
            - (3.0 * e_sq / 8.0 + 3.0 * e_sq * e_sq / 32.0 + 45.0 * (e_sq**3) / 1024.0)
            * math.sin(2.0 * lat_rad)
            + (15.0 * e_sq * e_sq / 256.0 + 45.0 * (e_sq**3) / 1024.0)
            * math.sin(4.0 * lat_rad)
            - (35.0 * (e_sq**3) / 3072.0) * math.sin(6.0 * lat_rad)
        )

        easting = k0 * n * (
            big_a
            + ((1.0 - t + c) * (big_a**3)) / 6.0
            + ((5.0 - 18.0 * t + t * t + 72.0 * c - 58.0 * ep_sq) * (big_a**5)) / 120.0
        ) + 500000.0

        northing = k0 * (
            m
            + n
            * tan_lat
            * (
                (big_a * big_a) / 2.0
                + ((5.0 - t + 9.0 * c + 4.0 * c * c) * (big_a**4)) / 24.0
                + ((61.0 - 58.0 * t + t * t + 600.0 * c - 330.0 * ep_sq) * (big_a**6)) / 720.0
            )
        )
        return round(easting, 3), round(northing, 3)


def validate_coordinates(record: dict[str, Any]) -> dict[str, Any]:
    lat = _to_float(record.get("latitude"))
    lon = _to_float(record.get("longitude"))
    flags: list[str] = []

    if lat is None or lon is None:
        flags.append("missing_or_invalid_coordinate")
        return {
            **record,
            "latitude": lat,
            "longitude": lon,
            "coord_status": "invalid",
            "coord_flags": flags,
            "crs": "EPSG:4326",
            "projected_crs": "EPSG:32643",
            "x_32643": None,
            "y_32643": None,
        }

    if (PUNE_LAT_MIN <= lon <= PUNE_LAT_MAX) and (PUNE_LON_MIN <= lat <= PUNE_LON_MAX):
        flags.append("swapped_lat_lon_suspected")

    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        flags.append("out_of_wgs84_bounds")
        return {
            **record,
            "latitude": lat,
            "longitude": lon,
            "coord_status": "invalid",
            "coord_flags": flags,
            "crs": "EPSG:4326",
            "projected_crs": "EPSG:32643",
            "x_32643": None,
            "y_32643": None,
        }

    in_pune_bbox = (PUNE_LAT_MIN <= lat <= PUNE_LAT_MAX) and (PUNE_LON_MIN <= lon <= PUNE_LON_MAX)
    if not in_pune_bbox:
        flags.append("outside_pune_district_bbox")

    x_32643, y_32643 = _wgs84_to_utm43n(lat, lon)
    coord_status = "valid_pune" if (in_pune_bbox and not flags) else "flagged"

    return {
        **record,
        "latitude": lat,
        "longitude": lon,
        "coord_status": coord_status,
        "coord_flags": flags,
        "crs": "EPSG:4326",
        "projected_crs": "EPSG:32643",
        "x_32643": x_32643,
        "y_32643": y_32643,
    }


def validate_station_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_coordinates(rec) for rec in records]
