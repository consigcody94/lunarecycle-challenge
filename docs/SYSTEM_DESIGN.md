# LunaRecycle Phase 2 - System Design Document

## Executive Summary

**System Name:** ARTEMIS-R (Advanced Recycling Technology for Extraterrestrial Material Integration System - Recycler)

**Core Innovation:** Hybrid Solar-Thermal Processing with Intelligent Material Routing

**Key Differentiators:**
1. **50% lower energy consumption** than pyrolysis-only systems via solar-thermal heating
2. **6 waste streams processed** (vs competitors' 2-3)
3. **Radiation shielding composites** as primary high-value output
4. **AI-driven adaptive processing** with real-time optimization
5. **Lunar environment integration** - leverages vacuum, thermal cycling, regolith ISRU

---

## 1. System Architecture

### 1.1 High-Level Overview

```
                              SOLAR CONCENTRATOR
                                     │
                                     ▼ (thermal energy)
┌──────────────────────────────────────────────────────────────────────────┐
│                         ARTEMIS-R PROCESSING UNIT                         │
│                                                                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌───────────┐ │
│  │   WASTE     │    │  MATERIAL   │    │  PROCESSING │    │  OUTPUT   │ │
│  │   INPUT     │───▶│  SORTING    │───▶│   MODULES   │───▶│  STORAGE  │ │
│  │   HOPPER    │    │  (AI+CV)    │    │             │    │           │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └───────────┘ │
│                                              │                           │
│                     ┌────────────────────────┼────────────────────────┐  │
│                     │                        │                        │  │
│                     ▼                        ▼                        ▼  │
│            ┌─────────────┐          ┌─────────────┐          ┌─────────┐│
│            │   THERMAL   │          │    MELT     │          │ MECHANICAL│
│            │  PROCESSOR  │          │  EXTRUSION  │          │ SHREDDER ││
│            │ (Pyrolysis) │          │  (Filament) │          │(Foam/Fiber)│
│            └─────────────┘          └─────────────┘          └─────────┘│
│                     │                        │                        │  │
│                     ▼                        ▼                        ▼  │
│            ┌─────────────┐          ┌─────────────┐          ┌─────────┐│
│            │  Syngas     │          │  3D Printer │          │Composite││
│            │  Biochar    │          │  Filament   │          │ Filler  ││
│            │  Pyro-oil   │          │             │          │         ││
│            └─────────────┘          └─────────────┘          └─────────┘│
│                     │                        │                        │  │
│                     └────────────────────────┴────────────────────────┘  │
│                                              │                           │
│                                              ▼                           │
│                                    ┌─────────────────┐                   │
│                                    │   COMPOSITE     │                   │
│                                    │  FABRICATION    │                   │
│                                    │   (+ Regolith)  │                   │
│                                    └─────────────────┘                   │
│                                              │                           │
│                                              ▼                           │
│                                    ┌─────────────────┐                   │
│                                    │ RADIATION       │                   │
│                                    │ SHIELDING       │                   │
│                                    │ PANELS          │                   │
│                                    └─────────────────┘                   │
└──────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
                              ┌─────────────────────────────┐
                              │      DIGITAL TWIN           │
                              │  - Real-time monitoring     │
                              │  - AI optimization          │
                              │  - Predictive maintenance   │
                              │  - VR/AR interface          │
                              └─────────────────────────────┘
```

### 1.2 Processing Modules

#### Module A: Thermal Processor (Solar-Assisted Pyrolysis)
- **Input:** Organic waste (food packaging, paper, cotton, hygiene items)
- **Process:** Low-temperature pyrolysis (350-450°C) with solar-thermal heating
- **Output:**
  - Syngas (H2, CO, CH4) → Fuel cells or heating
  - Biochar → Composite filler, water filtration
  - Pyrolysis oil → Chemical feedstock

#### Module B: Melt Extruder
- **Input:** Thermoplastics (LDPE, HDPE, PP, PET)
- **Process:** Melt extrusion at 180-280°C
- **Output:** 3D printer filament (1.75mm and 2.85mm)

#### Module C: Mechanical Processor
- **Input:** Foam (PVDF/Zotek), textiles, mixed composites
- **Process:** Low-temperature shredding and defibration
- **Output:**
  - Foam particles → Composite lightweight filler
  - Fiber strands → Insulation, reinforcement

#### Module D: Composite Fabricator
- **Input:** Biochar + foam particles + fiber + regolith
- **Process:** Compression molding with thermoplastic binder
- **Output:**
  - Radiation shielding panels
  - Structural tiles
  - Thermal insulation blocks

---

## 2. Waste Stream Processing Matrix

| Waste Item | Category | Mass % | Volume % | Primary Process | Secondary Process | Output Products |
|------------|----------|--------|----------|-----------------|-------------------|-----------------|
| Food Packaging Film | Food Packaging | 15% | 12% | Melt Extrusion | - | Filament |
| Metalized Film | Food Packaging | 8% | 6% | Thermal + Metal Sep | - | Syngas + Aluminum |
| Beverage Container | Food Packaging | 5% | 8% | Melt Extrusion | - | Filament |
| Cotton Clothing | Textiles | 12% | 10% | Mechanical Shred | Thermal | Fiber + Biochar |
| Synthetic Clothing | Textiles | 8% | 8% | Melt Extrusion | Mechanical | Filament + Fiber |
| Zotek F30 Foam | Protective | 10% | 30% | Mechanical Shred | Composite | Radiation Shield |
| Packaging Foam | Protective | 5% | 15% | Mechanical Shred | Composite | Insulation |
| Paper/Cardboard | Packaging | 10% | 5% | Thermal | - | Biochar + Syngas |
| Hygiene Wipes | Hygiene | 12% | 4% | Thermal | - | Biochar + Syngas |
| EVA Gloves | EVA Waste | 8% | 3% | Mechanical | Composite | Reinforced Panels |
| Tape/Adhesives | Misc | 3% | 1% | Thermal | - | Syngas |
| Filters (HEPA/AC) | Life Support | 4% | 2% | Mechanical | Composite | Shielding Filler |

---

## 3. Technical Specifications

### 3.1 System Dimensions & Mass

| Component | Dimensions (cm) | Mass (kg) | Power (W) |
|-----------|-----------------|-----------|-----------|
| Input Hopper + Sorter | 40 x 30 x 50 | 15 | 50 |
| Thermal Processor | 60 x 40 x 40 | 45 | 800* |
| Melt Extruder | 50 x 30 x 30 | 25 | 400 |
| Mechanical Shredder | 40 x 40 x 35 | 30 | 200 |
| Composite Press | 50 x 50 x 40 | 55 | 300 |
| Control System | 30 x 20 x 15 | 8 | 100 |
| Gas Management | 40 x 30 x 30 | 20 | 50 |
| Solar Concentrator | 150 x 150 x 20 | 25 | 0 |
| **TOTAL** | **~1.2 m³** | **223 kg** | **1,900 W peak** |

*Solar-thermal reduces electrical to ~300W when sun available

### 3.2 Performance Targets

| Metric | Target | Stretch Goal |
|--------|--------|--------------|
| Mass Recovery Rate | 90% | 95% |
| Energy Efficiency | 0.5 kWh/kg waste | 0.3 kWh/kg waste |
| Throughput | 8 kg/day | 12 kg/day |
| Crew Time | <30 min/week | <15 min/week |
| MTBF | 1 year | 2 years |
| Product Quality (filament) | ±0.05mm diameter | ±0.02mm |
| Shielding Effectiveness | 20% GCR reduction | 30% GCR reduction |

### 3.3 Energy Budget

**Daily Operation (processing 8 kg waste):**

| Phase | Duration | Power | Energy |
|-------|----------|-------|--------|
| Sorting & Shredding | 2 hr | 250 W | 0.5 kWh |
| Thermal Processing | 4 hr | 800 W* | 3.2 kWh |
| Melt Extrusion | 3 hr | 400 W | 1.2 kWh |
| Composite Fabrication | 2 hr | 300 W | 0.6 kWh |
| Control & Monitoring | 24 hr | 100 W | 2.4 kWh |
| **TOTAL** | - | - | **7.9 kWh/day** |

*With solar-thermal: reduces to ~1.5 kWh electrical

**Energy Recovery:**
- Syngas production: ~3 kg/day × 15 MJ/kg = 45 MJ = 12.5 kWh
- Net energy: +4.6 kWh/day (energy positive!)

---

## 4. PVDF/Zotek F30 Solution (Level 3 Challenge)

The Zotek F30 foam is the hardest material to recycle due to:
1. **PFAS content** - Releases toxic HF gas if heated above 450°C
2. **Closed-cell structure** - Difficult to compress or melt
3. **Low density** - Takes up 30% of volume but only 10% of mass

### 4.1 Our Solution: Cold Mechanical Processing

**Process:**
1. **Cryogenic pre-treatment** (optional): Use lunar night temperatures (-173°C) to embrittle foam
2. **Mechanical granulation**: Shred to 2-5mm particles at ambient temperature
3. **Static elimination**: Remove electrostatic charge that causes clumping
4. **Composite binding**: Mix with biochar + thermoplastic binder + regolith
5. **Compression molding**: Form into radiation shielding panels at <200°C

**Key Innovation:** Never heat PVDF above 200°C, preventing HF release entirely.

### 4.2 PVDF Composite Properties

| Property | Value | Comparison |
|----------|-------|------------|
| Density | 0.8-1.2 g/cm³ | 50% lighter than concrete |
| Hydrogen content | 8-12% by mass | Excellent neutron moderation |
| Thermal conductivity | 0.05 W/m·K | Superior insulation |
| Radiation attenuation | 15-25% GCR per 10cm | Competitive with polyethylene |
| Compressive strength | 20-40 MPa | Structural capability |

---

## 5. Output Products Specification

### 5.1 3D Printer Filament
- **Material:** Recycled LDPE/HDPE/PP blend
- **Diameter:** 1.75mm ± 0.05mm or 2.85mm ± 0.05mm
- **Tensile strength:** >20 MPa
- **Color:** Natural (translucent) or carbon-black
- **Applications:** Tools, brackets, containers, medical devices

### 5.2 Radiation Shielding Panels
- **Composition:** 40% biochar, 30% foam particles, 20% regolith, 10% binder
- **Dimensions:** 30cm × 30cm × 5cm standard tiles
- **Mass:** ~2 kg per tile
- **Shielding:** 20% GCR reduction per layer
- **Applications:** Habitat walls, storm shelter, equipment shielding

### 5.3 Syngas
- **Composition:** 40% H2, 35% CO, 20% CH4, 5% other
- **Heating value:** 15-18 MJ/kg
- **Production rate:** 2-4 kg/day
- **Applications:** Fuel cells, heating, chemical synthesis

### 5.4 Biochar
- **Carbon content:** >85%
- **Surface area:** 200-400 m²/g
- **Applications:**
  - Composite filler
  - Water filtration media
  - Soil amendment (for lunar agriculture)
  - CO2 adsorption

### 5.5 Structural Composites
- **Fiber-reinforced panels:** Cotton/synthetic fiber + thermoplastic matrix
- **Applications:** Non-load-bearing walls, equipment housings, furniture

---

## 6. Safety Systems

### 6.1 Atmospheric Control
- **Gas sensors:** H2, CO, CH4, HF, O2 continuous monitoring
- **Scrubber system:** Activated carbon + molecular sieve for emissions
- **Pressure relief:** Automatic venting to external vacuum if overpressure
- **Fire suppression:** CO2 flooding capability (no water/halon in space)

### 6.2 Thermal Safety
- **Multi-zone temperature monitoring:** 12 thermocouples throughout system
- **Automatic shutdown:** If any zone exceeds limits by 10%
- **Thermal runaway prevention:** Active cooling via heat pipes to radiator
- **Operator protection:** All hot surfaces enclosed, interlocked access

### 6.3 Mechanical Safety
- **Shredder interlock:** Cannot operate with access door open
- **Emergency stop:** Large red button, wireless backup
- **Pinch point guards:** All moving parts enclosed
- **Noise isolation:** <65 dB at operator position

### 6.4 PVDF-Specific Safety
- **Temperature lockout:** Thermal processor disabled if PVDF detected in stream
- **HF detector:** 0.1 ppm sensitivity, automatic shutdown
- **Separate processing path:** PVDF never enters thermal zone
- **Material passport:** AI tracks every gram of PVDF through system

---

## 7. Operational Modes

### 7.1 Autonomous Mode (Normal)
- AI manages all sorting, processing, and product fabrication
- Crew interaction: Load waste hopper daily (~8 kg)
- Crew time: <5 minutes/day
- Alerts only for maintenance or anomalies

### 7.2 Supervised Mode
- Crew monitors via dashboard during operation
- Manual override capability for all functions
- Used during initial deployment or troubleshooting
- Crew time: ~30 minutes/day

### 7.3 Manual Mode
- Direct crew control of each subsystem
- Used for maintenance, calibration, or special processing
- Crew time: 2-4 hours as needed

### 7.4 Safe Mode
- Activated by any safety interlock
- All heating disabled
- Gas management continues
- Crew notification immediate
- Requires crew acknowledgment to resume

---

## 8. Maintenance Schedule

| Interval | Tasks | Time | Parts Required |
|----------|-------|------|----------------|
| Daily | Empty product bins, load waste | 5 min | None |
| Weekly | Clean input hopper, check filters | 15 min | None |
| Monthly | Replace gas scrubber media | 30 min | Scrubber cartridge |
| Quarterly | Lubricate mechanical systems | 1 hr | Lubricant |
| Annually | Replace extruder nozzle, seals | 4 hr | Nozzle, seal kit |
| 2 Years | Major overhaul | 8 hr | Comprehensive kit |

**Estimated consumables mass:** 5 kg/year

---

## 9. Lunar Environment Adaptations

### 9.1 Vacuum Utilization
- **Outgassing:** Use lunar vacuum to remove volatiles from feedstock
- **Sublimation drying:** Remove moisture without heating
- **Pressure differential:** Drive gas flows without pumps

### 9.2 Thermal Cycling
- **Night cooling:** Use -173°C for cryogenic processing
- **Day heating:** Solar-thermal concentration reduces electrical needs
- **Thermal mass:** Buffer temperature swings with phase-change materials

### 9.3 Reduced Gravity (1/6 g)
- **Settling:** Slower particle settling affects separation
- **Convection:** Reduced natural convection in thermal zones
- **Mixing:** Enhanced mechanical mixing required
- **Extrusion:** Lower pressure needed for same flow rate

### 9.4 Radiation Environment
- **Material degradation:** UV-stabilized polymers for external components
- **Electronics hardening:** Rad-hard or COTS with shielding
- **Product quality:** Radiation-induced crosslinking may improve strength

### 9.5 Regolith Integration (ISRU)
- **Composite filler:** 20-30% regolith improves radiation shielding
- **Mold material:** Pressed regolith molds for casting
- **Sintering:** Solar-sintered regolith for structural applications

---

## 10. Digital Twin Architecture

### 10.1 Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     DIGITAL TWIN PLATFORM                        │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   SENSOR    │  │   PHYSICS   │  │     AI      │             │
│  │   LAYER     │  │   ENGINE    │  │   ENGINE    │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                      │
│                          ▼                                      │
│                 ┌─────────────────┐                             │
│                 │   DATA FUSION   │                             │
│                 │     ENGINE      │                             │
│                 └────────┬────────┘                             │
│                          │                                      │
│         ┌────────────────┼────────────────┐                     │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ DASHBOARD   │  │  VR/AR      │  │  ALERTING   │             │
│  │ (2D Web)    │  │ INTERFACE   │  │  SYSTEM     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Sensor Integration
- **Temperature:** 12 thermocouples (K-type, ±1°C)
- **Pressure:** 4 transducers (0-500 kPa, ±0.5%)
- **Mass flow:** 3 load cells (0-50 kg, ±10g)
- **Gas composition:** NDIR + electrochemical sensors
- **Visual:** 2 cameras (input hopper, product output)
- **Power:** Voltage, current, energy metering

### 10.3 Physics Simulation
- **Thermal model:** Finite element heat transfer
- **Material flow:** Discrete element method for particles
- **Chemical kinetics:** Pyrolysis reaction modeling
- **Mechanical:** Stress/strain in composite pressing
- **Update rate:** 10 Hz for real-time tracking

### 10.4 AI/ML Capabilities
- **Waste classification:** CNN for material identification (95%+ accuracy)
- **Process optimization:** Reinforcement learning for parameter tuning
- **Predictive maintenance:** LSTM for failure prediction (7-day horizon)
- **Quality prediction:** Regression models for product properties
- **Anomaly detection:** Autoencoder for unusual patterns

### 10.5 User Interfaces
- **Web Dashboard:** Real-time metrics, alerts, historical trends
- **VR Mode:** Immersive 3D view of system internals
- **AR Mode:** Overlay maintenance instructions on physical hardware
- **Voice Control:** Hands-free operation commands
- **Mobile App:** Remote monitoring and notifications

---

## 11. Development Roadmap

### Phase 2A: Milestone Round (Due: January 22, 2026)

**Deliverables:**
1. Detailed design documentation (this document)
2. Functional prototype of ONE processing module (Thermal or Melt)
3. Digital twin with basic simulation
4. Test data from 10+ processing runs
5. Video demonstration (5-10 minutes)

**Schedule:**
- Months 1-2: Component procurement, mechanical assembly
- Months 3-4: Electronics integration, software development
- Month 5: Testing and validation
- Month 6: Documentation and submission

### Phase 2B: Final Round (Due: August 2026)

**Deliverables:**
1. Integrated prototype with all 4 modules
2. Full digital twin with AI capabilities
3. Processing demonstration of all 6 waste streams
4. 100+ hours of operation data
5. Sample products for evaluation
6. In-person demonstration at NASA facility

**Schedule:**
- Months 7-9: Full system integration
- Months 10-11: Extended testing, optimization
- Month 12: Final documentation, shipping

---

## 12. Budget Estimate

### 12.1 Prototype Build

| Category | Items | Cost |
|----------|-------|------|
| Mechanical | Frame, motors, gearboxes, bearings | $8,000 |
| Thermal | Heating elements, insulation, heat exchangers | $5,000 |
| Electronics | Sensors, controllers, wiring | $4,000 |
| Computing | Industrial PC, displays, networking | $3,000 |
| Safety | Gas sensors, interlocks, enclosures | $2,000 |
| Materials | Feedstock, consumables, test samples | $1,500 |
| Tools | Fabrication equipment, test instruments | $2,500 |
| Software | Licenses, cloud services | $1,000 |
| **Subtotal** | | **$27,000** |

### 12.2 Operations

| Category | Monthly Cost |
|----------|-------------|
| Lab space | $500 |
| Utilities | $200 |
| Consumables | $300 |
| Cloud computing | $100 |
| **Monthly Total** | **$1,100** |

### 12.3 Total Project Cost

| Phase | Duration | Cost |
|-------|----------|------|
| Phase 2A (Milestone) | 6 months | $33,600 |
| Phase 2B (Final) | 6 months | $25,000 |
| Contingency (20%) | - | $11,720 |
| **TOTAL** | 12 months | **$70,320** |

---

## 13. Team Requirements

### Core Team (Minimum)
1. **Systems Engineer** - Integration, testing, documentation
2. **Mechanical Engineer** - Fabrication, assembly, thermal systems
3. **Software Engineer** - Digital twin, AI/ML, interfaces
4. **Materials Scientist** - Composite development, testing

### Advisors (Recommended)
- NASA/aerospace industry mentor
- Pyrolysis/waste processing expert
- Space systems reliability specialist

---

## 14. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pyrolysis temperature control | Medium | High | Multiple thermocouples, PID tuning |
| PVDF HF release | Low | Critical | Never heat above 200°C, HF sensors |
| Filament quality inconsistent | Medium | Medium | In-line diameter monitoring, feedback control |
| Composite strength inadequate | Medium | Medium | Iterative mix optimization, testing |
| Digital twin accuracy | Medium | Low | Calibration with real data, uncertainty quantification |
| Schedule delay | High | Medium | Parallel development, early procurement |
| Budget overrun | Medium | Medium | 20% contingency, phased spending |
| Component failure | Low | High | Spares for critical items, modular design |

---

## 15. Success Criteria

### Minimum Viable Product (MVP)
- [ ] Process 3+ waste streams successfully
- [ ] Achieve 80% mass recovery rate
- [ ] Produce usable filament (printable)
- [ ] Operate for 10 hours continuously
- [ ] Digital twin tracks mass/energy balance

### Target Performance
- [ ] Process all 6 waste streams
- [ ] Achieve 90% mass recovery rate
- [ ] Produce radiation shielding panels
- [ ] Operate for 100 hours total
- [ ] AI optimization improves efficiency by 10%

### Stretch Goals
- [ ] Energy positive operation (net energy production)
- [ ] 95% mass recovery rate
- [ ] VR/AR interface fully functional
- [ ] Demonstrate 3 recycling cycles of same material
- [ ] Regolith simulant integration tested

---

## Appendices

- **Appendix A:** Detailed CAD Drawings
- **Appendix B:** Bill of Materials
- **Appendix C:** Software Architecture
- **Appendix D:** Test Protocols
- **Appendix E:** Safety Data Sheets
- **Appendix F:** NASA Challenge Requirements Compliance Matrix

---

*Document Version: 1.0*
*Last Updated: 2025-11-30*
*Classification: Competition Sensitive*
