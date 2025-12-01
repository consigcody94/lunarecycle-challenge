# LunaRecycle Challenge - Lunar Waste Recycling Simulation

A comprehensive simulation system for modeling waste management and recycling processes for NASA's LunaRecycle Challenge. This project provides tools for analyzing non-metabolic waste streams, evaluating recycling technologies, and optimizing resource recovery for long-duration lunar missions.

## Overview

NASA's LunaRecycle Challenge is a $3 million competition focused on developing recycling solutions for lunar missions. This simulation system supports:

- **Waste Stream Modeling**: Categorization and tracking of non-metabolic waste (food packaging, clothing, foam, hygiene items)
- **Recycling Technology Simulation**: Pyrolysis, plasma processing, thermochemical conversion models
- **Mass/Energy Balance Analysis**: Track material flows, energy requirements, and recovery efficiency
- **Lunar Environment Simulation**: Model constraints of lunar surface operations (1/6g, thermal cycling, radiation)
- **Digital Twin Support**: Generate simulation data compatible with challenge requirements

## Key Metrics (Based on NASA Research)

| Parameter | Value | Source |
|-----------|-------|--------|
| Waste generation rate | ~2 kg/astronaut/day | NASA TCPS |
| Annual waste (4-crew) | 2,100-2,600 kg | NASA LunaRecycle |
| Food packaging | ~21% of solid waste | ISS data |
| Packing material | ~30% of cargo volume | NASA Alternative Packaging Study |

## Project Structure

```
lunarecycle-challenge/
├── src/
│   ├── waste/              # Waste stream definitions and models
│   ├── recycling/          # Recycling technology simulations
│   ├── environment/        # Lunar environment parameters
│   ├── simulation/         # Core simulation engine
│   └── analysis/           # Analysis and reporting tools
├── data/
│   ├── materials/          # Material property databases
│   ├── waste_streams/      # Waste composition data
│   └── scenarios/          # Mission scenario configurations
├── tests/                  # Verification and validation tests
├── docs/                   # Documentation
└── examples/               # Example simulations and notebooks
```

## Installation

```bash
# Clone the repository
git clone https://github.com/consigcody94/lunarecycle-challenge.git
cd lunarecycle-challenge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

## Quick Start

```python
from lunarecycle import Simulation, WasteStream, RecyclingSystem

# Create a 4-crew lunar mission scenario
sim = Simulation(
    crew_size=4,
    mission_duration_days=365,
    location="lunar_surface"
)

# Add waste streams
sim.add_waste_stream(WasteStream.FOOD_PACKAGING)
sim.add_waste_stream(WasteStream.CLOTHING)
sim.add_waste_stream(WasteStream.FOAM_PACKAGING)

# Configure recycling system
recycler = RecyclingSystem(
    technology="pyrolysis",
    processing_capacity_kg_day=5.0
)
sim.add_recycling_system(recycler)

# Run simulation
results = sim.run()
print(f"Recovery efficiency: {results.recovery_efficiency:.1%}")
print(f"Mass reduction: {results.mass_reduction:.1%}")
```

## Waste Categories (Per NASA LunaRecycle)

The challenge focuses on **non-metabolic, non-biological** solid waste:

1. **Food Packaging** - Plastic films, foil pouches, retort packaging
2. **Clothing** - Cotton, synthetic fabrics (no laundry in space)
3. **Foam/Packing** - Protective materials, cargo padding
4. **Hygiene Items** - Wipes, towels (dry)
5. **Science Materials** - Experiment consumables, sample containers
6. **General Waste** - Tape, paper, filters

## Recycling Technologies Modeled

- **Pyrolysis**: Thermal decomposition (300-700°C), converts polymers to syngas/char
- **Plasma Arc**: High-temperature (10,000-20,000°C) vaporization
- **Microwave-Assisted**: Selective heating for targeted material breakdown
- **Heat Melt Compaction**: Volume reduction with water recovery
- **Mechanical Recycling**: Shredding, melting, reforming plastics

## Lunar Environment Parameters

| Parameter | Lunar Surface | Inside Habitat |
|-----------|---------------|----------------|
| Gravity | 1.62 m/s² (1/6 Earth) | 1.62 m/s² |
| Temperature | -173°C to +127°C | 20-25°C |
| Pressure | Near vacuum | ~101 kPa |
| Radiation | High | Shielded |

## Challenge Constraints

Per NASA LunaRecycle Challenge Phase 2:
- **No incineration/burning** of waste
- **No PFAS release** or microplastic generation
- Must **transform** waste (not just reuse)
- Minimize system **mass and volume**
- Maximize **energy efficiency**

## References

- [NASA LunaRecycle Challenge](https://www.nasa.gov/prizes-challenges-and-crowdsourcing/centennial-challenges/lunarecycle/)
- [LunaRecycle FAQ](https://lunarecyclechallenge.ua.edu/frequently-asked-questions/)
- [NASA Trash Compaction Processing System](https://www.nasa.gov/ames/space-biosciences/bioengineering-branch/the-trash-compaction-processing-system/)
- [Waste Management Options for Long-Duration Space Missions](https://ntrs.nasa.gov/citations/20140010284)

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting PRs.
