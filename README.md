# EV-Bharat Drishti

**Spatial EV Infrastructure Planning Engine**

EV-Bharat Drishti is an open-source, evidence-based spatial decision-support platform for identifying charging gaps and prioritising public EV charging locations in India. It combines EV registration data, charger listings, road-network accessibility and grid constraints into one auditable planning view.

> **Status:** Concept and prototype roadmap for Techfest 2026-27, Challenge 1: EV Infra Map India. The Pune pilot figures in this repository concept are prototype outputs and are **not validated results**.

## Project Objectives

- Create a unified, deduplicated public-charging station registry.
- Estimate daily charging demand using vehicle-segment duty cycles.
- Identify EV charging gaps with a 0-100 Gap Assessment Index (GAI).
- Recommend charging hubs using a budget-constrained Maximal Covering Location Problem (MCLP).
- Use real road-network isochrones instead of straight-line buffers.
- Provide PM E-DRIVE what-if analysis and exportable planning outputs.

## Pune District Pilot

The initial pilot geography is Pune District, Maharashtra. Pune is representative of varied EV infrastructure needs:

- Urban and suburban two-wheeler demand
- Last-mile three-wheeler and cargo activity
- Municipal bus operations
- IT and commercial centres
- Industrial corridors
- Expressway and intercity travel
- Rural and agro-industrial areas

Prototype pilot outputs include 10 planning zones, 243 deduplicated active chargers and 6 recommended candidate hubs. These values require source reconciliation and independent validation.

## Key Features

### Unified Charger Registry

Merge charger listings from EV Yatra, OpenStreetMap and participating operators into a canonical station table. Spatial deduplication uses DBSCAN with a 50-metre radius to prevent duplicate listings from inflating charging capacity.

### Segmented Energy-Demand Model

Estimate public-charging demand from registered fleet counts and segment-specific vehicle movement, energy intensity and public-charging dependency:

```text
Demand = sum over vehicle segments of
registered EVs x daily kilometres x kWh per kilometre x public-charging share
```

The duty-cycle assumptions are proposed and must be calibrated with ICAT/ARAI test data, operator telemetry and fleet information.

### Gap Assessment Index

The proposed GAI combines normalised:

| Component | Weight | Meaning |
|---|---:|---|
| Public-energy deficit | 35% | Estimated unmet daily public-charging demand |
| EV-to-charger ratio | 25% | Relative charging scarcity |
| Traffic | 25% | Road and transit throughput |
| Grid risk | 15% | Substation distance or capacity constraint |

GAI ranges from 0 (saturated) to 100 (critical charging desert). Weights and thresholds are proposal assumptions and will require sensitivity testing.

### MCLP Siting Optimiser

An integer linear programme selects candidate locations that maximise weighted demand coverage under a budget:

- 5 km drive-time radius for urban locations
- 25 km drive-time radius for expressway locations
- Candidate sites include fuel outlets, toll plazas and multimodal transport hubs
- PuLP and COIN-OR CBC are the proposed optimisation tools

### Interactive Decision GIS

The planned interface is based on MapLibre or Leaflet and will support:

- GAI choropleth and charger layers
- Drive-time catchments
- Proposed hub locations
- Vehicle-segment filters
- PM E-DRIVE budget scenarios
- GeoJSON and policy brief exports

## Proposed System Architecture

```text
Data ingestion -> Cleaning and deduplication -> Spatial analytics -> Decision GIS

VAHAN 4, EV Yatra, OSM, operator feeds
                    |
                    v
       CRS standardisation + PostGIS
                    |
                    v
  Demand model + GAI + MCLP optimisation
                    |
                    v
    Map, what-if simulator, briefs/export
```

**Planned data and application stack**

- Python, Pandas, NumPy and scikit-learn
- PostgreSQL/PostGIS
- GeoPandas, Shapely and NetworkX
- OSRM road routing
- PuLP and COIN-OR CBC
- FastAPI or Streamlit
- Leaflet or MapLibre GL

## Data Sources

| Source | Status | Intended use |
|---|---|---|
| VAHAN 4 dashboard | Conditional | EV registrations by RTO and vehicle class |
| BEE EV Yatra | Conditional | Public charger directory |
| OpenStreetMap, Overpass, Geofabrik | Open | Roads and points of interest |
| OGD Platform India | Open, licence varies | Supplementary spatial and mobility datasets |
| CEA / Ministry of Power | Open | Grid statistics and policy guidance |
| MSEDCL / DISCOM | Restricted | Feeder headroom and grid constraints |
| Operator apps/APIs | Restricted | Charger listings and live availability |
| PM Gati Shakti | Unverified | Logistics and freight spatial layers |
| ICAT / ARAI | Unverified | Validation benchmarks and duty-cycle calibration |
| PMPML | Unverified | Depot, bus and operating-data reconciliation |

Before any production use, teams must verify source terms, document licences and obtain the permissions needed for restricted or conditional datasets.

## Validation and Reconciliation

The concept explicitly distinguishes completed arithmetic checks from future data validation:

- [x] Prototype EV-to-charger ratio arithmetic
- [x] Candidate-hub capex total
- [x] GAI weight total
- [ ] Calibrate VMT, energy intensity and public-charging share
- [ ] Reconcile charger records across independent sources
- [ ] Back-test demand against operator utilisation
- [ ] Test GAI weight sensitivity
- [ ] Report MCLP optimality and budget stability
- [ ] Confirm PMPML e-bus count with the operator
- [ ] Obtain grid headroom data

## Prototype Notes

Several figures in the original concept document are illustrative:

- 186,907 registered EVs
- 243 active deduplicated chargers
- 769:1 EV-to-charger ratio
- 145.3 MWh modelled daily deficit
- Six MCLP candidate hubs
- Six hub capex estimate of INR 4.73 crore

These values are not independently verified. The prototype dashboard layout and schematic Pune map are conceptual designs.

## Scalability Roadmap

1. Pune District: 10 prototype zones and 3 RTO regions
2. Maharashtra: all state districts and RTO regions
3. Priority freight and highway corridors
4. All 36 States and Union Territories

Nationwide deployment depends on data-sharing arrangements, source validation and an independently auditable update process.

## Development Status

This repository currently contains the project concept and README. The ETL pipeline, spatial database, optimisation engine and interactive UI have been proposed but are not yet included as an implemented application.

To contribute:

1. Add data ingestion scripts and source documentation.
2. Define schemas and provenance for the canonical charger registry.
3. Implement and test the segmented demand model.
4. Implement GAI calculation and sensitivity analysis.
5. Add MCLP with fixed, documented assumptions.
6. Build and validate the Pune web GIS prototype.

## Repository

- **Team:** GridNexus
- **Team ID:** TM-65D8DD15DAF
- **Competition:** Techfest 2026-27, IIT Bombay
- **Challenge:** Challenge 1 - EV Infra Map India
- **Institution:** Hindi Seva Mandal's Shri Sant Gadge Baba College of Engineering and Technology, Bhusawal


## License

The project is described as 100% open-source. A repository license has not yet been selected or added. Add an appropriate `LICENSE` file before distributing implementation code or datasets.
