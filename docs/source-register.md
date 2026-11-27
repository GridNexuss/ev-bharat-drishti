# EV-Bharat Drishti — Permitted Data Sources & Provenance Register

**Owner:** Tanveer (Data Engineering & ETL)  
**Pilot Geography:** Pune District, Maharashtra, India  
**Status:** Draft for `GDX-003` (Prototype MVP — unverified and restricted sources explicitly flagged)

## 1. Data Integrity Rules for ETL
- **No fabricated data:** Never invent station records, vehicle registration counts, candidate site costs, or grid headroom.
- **Separate reported vs. verified status:** A charger listed as operational by an external source is `unverified` until independently checked.
- **No silent zero-filling:** Missing or restricted grid/capacity evidence remains `unknown` or `null` (never converted to `0`).
- **Preserve provenance:** Every record keeps `source_name`, `source_url`, `access_classification`, `licence_or_access_basis`, `fetched_at`, `effective_date`, and `source_record_id`.

## 2. Access Classification Definitions
- **OPEN:** Publicly available under open/published terms (e.g., OpenStreetMap under ODbL, permitted OGD datasets, published MHI/MoP/BEE/ICAT/ARAI documents).
- **CONDITIONAL:** Public portal/directory where bulk-download, API, or terms of use must be checked before automated or large-scale collection (e.g., VAHAN 4 dashboard, BEE EV-Yatra).
- **RESTRICTED:** Requires explicit permission, partnership, or formal agreement/MoU (e.g., private operator feeds, MSEDCL/DISCOM feeder headroom data).
- **UNVERIFIED:** Access route, exact dataset, or current figures not yet confirmed (e.g., PMPML current e-bus figures, PM Gati Shakti external access).

## 3. Source Register Summary

| Source ID | Source Name | Access | Licence / Access Basis | Coverage | Retrieval Date | Key Limitation |
|---|---|---|---|---|---|---|
| `SRC-OSM-01` | OpenStreetMap | `OPEN` | ODbL (attribution + share-alike) | Pune / India | 2026-11-27 | Community data; verify accuracy and duplicates |
| `SRC-OGD-02` | OGD Platform India | `OPEN` | Per-dataset licence (e.g., GODL-India) | India / State / District | 2026-11-27 | Check dataset-level licence and coverage date |
| `SRC-VAHAN-03` | VAHAN 4 Dashboard | `CONDITIONAL` | Permitted exports only; no open bulk API | Pune RTOs / India | 2026-11-27 | Respect terms; track MH-12 to MH-61 transition |
| `SRC-EVYATRA-04` | BEE EV-Yatra | `CONDITIONAL` | Confirm bulk/reuse terms | India / Pune | 2026-11-27 | Reported status unverified; check duplicates |
| `SRC-CPO-05` | CPO Feeds | `RESTRICTED` | Permission / partnership / OCPI feed | Operator networks | 2026-11-27 | Restricted access; not assumed open |
| `SRC-MSEDCL-06` | MSEDCL / DISCOM Grid | `RESTRICTED` | MoU / formal request | Pune / Maharashtra | 2026-11-27 | Restricted feeder data; keep missing as unknown |
| `SRC-PMPML-07` | PMPML Fleet & Depots | `UNVERIFIED` | Confirm directly with PMPML | Pune / PCMC | 2026-11-27 | Conflicting public counts; needs confirmation |
| `SRC-POLICY-08` | MHI/MoP/BEE/ICAT/ARAI | `OPEN` | Published public guidelines & reports | National / MH | 2026-11-27 | Check benchmark applicability before use |
| `SRC-GATISHAKTI-09` | PM Gati Shakti | `UNVERIFIED` | External access unverified | National | 2026-11-27 | External layer access not yet verified |

## 4. Handoff Notes for Teammates
- **Apurva:** Align `data_sources` schema and provenance fields with `services/etl/sources/source_register.yaml`.
- **Ayesha:** Use `SRC-VAHAN-03`, `SRC-PMPML-07`, and `SRC-POLICY-08` access/calibration notes for demand and GAI inputs.
- **Anas:** Use `SRC-OSM-01` and `SRC-MSEDCL-06` notes for candidate locations and grid-constraint caveats.
- **Dhruv:** Keep source provenance and access/verification status visible in the UI.
