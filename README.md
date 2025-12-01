# ARTEMIS-R: Advanced Recycling Technology for Extraterrestrial Material Integration System

A complete recycling solution for NASA's LunaRecycle Challenge Phase 2, featuring a hybrid solar-thermal waste processing system with digital twin simulation.

## Challenge Overview

NASA's LunaRecycle Challenge is a $3 million competition focused on developing recycling solutions for lunar missions. This repository contains:

- **Complete System Design** - Hybrid solar-thermal processing architecture
- **Digital Twin** - Full physics simulation with AI/ML capabilities
- **Prototype Specifications** - CAD-ready designs and bill of materials
- **Safety Systems** - PVDF-safe processing with comprehensive interlocks
- **Submission Documentation** - Ready for NASA Phase 2 submission

## Key Innovation: PVDF Safety Solution

The Level 3 Challenge (Zotek F30 PVDF foam) releases toxic HF gas when heated. Our solution:

1. **Cold Mechanical Processing** - Never heat PVDF above 200°C
2. **Particle Integration** - Incorporate shredded foam into composites
3. **Low-Temperature Pressing** - Form radiation shielding tiles safely

**Result:** Zero HF release, 100% PVDF utilization

## System Architecture

```
                     ┌──────────────────────────────────────┐
                     │         ARTEMIS-R System             │
                     │                                      │
  Waste Input  ──────►  IHA-100: Input Hopper/Classifier   │
                     │           │                          │
                     │     ┌─────┼─────┬─────┐             │
                     │     ▼     ▼     ▼     ▼             │
                     │  TPR-200  MEX-300  MSH-400          │
                     │  Thermal  Melt     Mechanical       │
                     │  Process  Extruder Shredder         │
                     │     │       │       │               │
                     │     └───────┴───────┘               │
                     │             │                        │
                     │             ▼                        │
                     │       CPR-500: Composite Press      │
                     │             │                        │
                     │             ▼                        │
                     │    Products: Filament, Tiles,       │
                     │    Syngas, Biochar, Water           │
                     └──────────────────────────────────────┘
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Mass Recovery Rate | 90%+ |
| Net Energy Balance | POSITIVE (+44 kWh/week) |
| Crew Time | <30 min/week |
| PVDF Safety | Zero thermal processing |
| Throughput | 8 kg/day |
| Total System Mass | 223 kg |

## Products Generated

- **3D Printer Filament** - For on-demand manufacturing
- **Radiation Shielding Tiles** - Composites with foam, biochar, regolith
- **Syngas Fuel** - For energy recovery (4.2 kWh/batch)
- **Biochar** - For filtration and composites
- **Recovered Water** - From thermal processing

## Project Structure

```
lunarecycle-challenge/
├── src/lunarecycle/
│   ├── artemis/           # ARTEMIS-R system modules
│   │   ├── modules.py     # Processing modules (TPR, MEX, MSH, CPR)
│   │   ├── system.py      # Integrated system coordinator
│   │   ├── control.py     # Control system & safety interlocks
│   │   └── digital_twin.py # Physics & AI simulation
│   ├── dashboard/         # Visualization dashboard
│   ├── waste/             # Waste stream definitions
│   ├── recycling/         # Generic recycling processes
│   ├── environment/       # Lunar environment models
│   └── simulation/        # Core simulation engine
├── tests/                 # 109 automated tests
├── docs/
│   ├── SYSTEM_DESIGN.md   # Complete technical specification
│   ├── CAD_SPECIFICATIONS.md # Prototype drawings
│   ├── BILL_OF_MATERIALS.md  # $32,100 budget breakdown
│   └── NASA_SUBMISSION.md    # Challenge submission document
└── README.md
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/lunarecycle-challenge.git
cd lunarecycle-challenge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

## Quick Start

### Run the Digital Twin Dashboard

```bash
# Console dashboard (no dependencies)
python -m lunarecycle.dashboard.app

# Web dashboard (requires dash/plotly)
pip install dash plotly
python -m lunarecycle.dashboard.app --web
```

### Run Simulation

```python
from lunarecycle.artemis import DigitalTwin

# Create and run digital twin
twin = DigitalTwin()
twin.start_simulation()

# Simulate 7 days of operation
for day in range(7):
    result = twin.simulate_processing_day()
    print(f"Day {day+1}: {result['final_metrics']}")

# Get visualization data
data = twin.get_visualization_data()
print(f"Mass Recovery: {data['metrics']['mass_recovery']:.1%}")
print(f"Net Energy: {data['metrics']['net_energy_kwh']:.1f} kWh")
```

### Run ARTEMIS System Directly

```python
from lunarecycle.artemis.system import run_artemis_simulation

# Run 30-day simulation
system = run_artemis_simulation(crew_size=4, days=30, solar_available=True)

# Get results
products = system.get_product_summary()
energy = system.get_energy_summary()

print(f"Total Products: {products['total_kg']:.1f} kg")
print(f"Net Energy: {energy['net_kwh']:.1f} kWh")
```

## Testing

```bash
# Run all tests (109 tests)
pytest tests/ -v

# Run only ARTEMIS tests
pytest tests/test_artemis.py -v

# Run with coverage
pytest tests/ --cov=lunarecycle
```

## Waste Categories Supported

| Category | Processing Route | Products |
|----------|-----------------|----------|
| Food Packaging Film | Melt Extruder | 3D Filament |
| Metalized Film | Thermal + Separation | Syngas + Metal |
| Cotton Clothing | Shredder + Thermal | Fiber + Biochar |
| Synthetic Clothing | Melt Extruder | Filament |
| Zotek F30 Foam (PVDF) | **Mechanical Only** | Shield Filler |
| Paper/Cardboard | Thermal | Biochar + Syngas |
| Hygiene Wipes | Thermal | Biochar + Syngas |

## Safety Features

- **HF Detection Interlock** - 0.1 ppm triggers immediate shutdown
- **Over-Temperature Protection** - 500°C max reactor limit
- **Over-Pressure Relief** - 300 kPa automatic venting
- **E-Stop System** - 3 locations, global shutdown
- **Door Interlocks** - Prevents operation with access open

## Digital Twin Capabilities

- **Physics Simulation** - Heat transfer, pyrolysis kinetics, mass balance
- **AI/ML Engine** - Waste classification, anomaly detection, predictive maintenance
- **Real-Time Monitoring** - 25+ sensor channels
- **Visualization** - Web dashboard with charts and status displays
- **State Export** - JSON format for data analysis

## Lunar Adaptation Path

| Earth Prototype | Lunar Version |
|-----------------|---------------|
| Grid power | Solar + nuclear backup |
| Air cooling | Radiative cooling to vacuum |
| Manual loading | Robotic material handling |
| 8 kg/day | 20 kg/day throughput |

## Budget Summary

| Category | Cost |
|----------|------|
| Mechanical Components | $8,450 |
| Thermal System | $5,200 |
| Electronics & Sensors | $4,100 |
| Computing & Control | $3,200 |
| Safety Equipment | $1,800 |
| Materials & Consumables | $1,500 |
| Tools & Test Equipment | $2,500 |
| **Contingency (20%)** | $5,350 |
| **TOTAL** | **$32,100** |

## References

- [NASA LunaRecycle Challenge](https://www.nasa.gov/prizes-challenges-and-crowdsourcing/centennial-challenges/lunarecycle/)
- [LunaRecycle FAQ](https://lunarecyclechallenge.ua.edu/frequently-asked-questions/)
- [NASA TCPS](https://www.nasa.gov/ames/space-biosciences/bioengineering-branch/the-trash-compaction-processing-system/)

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Prepared for NASA LunaRecycle Challenge Phase 2*
*Submission Deadline: January 22, 2026*
