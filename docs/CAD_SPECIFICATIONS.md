# ARTEMIS-R CAD Specifications

## 1. Overall Assembly

### 1.1 System Envelope
```
┌────────────────────────────────────────────────────────────────┐
│                    TOP VIEW (1200mm x 800mm)                    │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  INPUT   │  │ THERMAL  │  │   MELT   │  │COMPOSITE │       │
│  │  HOPPER  │  │PROCESSOR │  │ EXTRUDER │  │  PRESS   │       │
│  │  300x400 │  │  400x600 │  │  300x500 │  │  500x500 │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│       │              │              │              │           │
│       └──────────────┴──────────────┴──────────────┘           │
│                    CONVEYOR SYSTEM (1000mm)                    │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │   MECHANICAL     │  │    CONTROL       │                    │
│  │   SHREDDER       │  │    CABINET       │                    │
│  │   400x400        │  │    300x200       │                    │
│  └──────────────────┘  └──────────────────┘                    │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                   FRONT VIEW (1200mm x 900mm)                   │
│                                                                 │
│            ┌─────────────────────────────────┐                 │
│            │     SOLAR CONCENTRATOR          │  (deployable)   │
│            │     1500 x 1500mm               │                 │
│            └─────────────────────────────────┘                 │
│                          │                                      │
│  ┌─────┐  ┌─────────────┬┴┬─────────────┐  ┌─────┐            │
│  │INPUT│  │   THERMAL PROCESSOR         │  │ MELT │            │
│  │ 500 │  │        400mm H              │  │ 300  │            │
│  │  H  │  │                             │  │  H   │            │
│  └─────┘  └─────────────────────────────┘  └─────┘            │
│     │                   │                      │               │
│  ┌──┴───────────────────┴──────────────────────┴──┐            │
│  │              BASE FRAME (900mm x 600mm)         │            │
│  │              Height: 100mm                      │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Dimensions Summary

| Module | Length (mm) | Width (mm) | Height (mm) | Mass (kg) |
|--------|-------------|------------|-------------|-----------|
| Input Hopper Assembly | 400 | 300 | 500 | 15 |
| Thermal Processor | 600 | 400 | 400 | 45 |
| Melt Extruder | 500 | 300 | 300 | 25 |
| Mechanical Shredder | 400 | 400 | 350 | 30 |
| Composite Press | 500 | 500 | 400 | 55 |
| Control Cabinet | 300 | 200 | 150 | 8 |
| Gas Management | 400 | 300 | 300 | 20 |
| Base Frame | 1200 | 800 | 100 | 25 |
| **TOTAL ENVELOPE** | **1200** | **800** | **900** | **223** |

---

## 2. Input Hopper Assembly (IHA-100)

### 2.1 Overview
The input hopper receives unsorted waste and performs AI-assisted classification and routing.

### 2.2 Components

```
IHA-100 INPUT HOPPER ASSEMBLY
│
├── IHA-110 Hopper Body
│   ├── IHA-111 Main Chamber (SS316, 300x400x400mm)
│   ├── IHA-112 Lid Assembly (hinged, safety interlock)
│   ├── IHA-113 Viewing Window (polycarbonate, 150x100mm)
│   └── IHA-114 Load Cell Mount (4x corner mounts)
│
├── IHA-120 Classification System
│   ├── IHA-121 Camera Mount (RGB + NIR camera)
│   ├── IHA-122 LED Ring Light (360°, 24V DC)
│   ├── IHA-123 Turntable (stepper motor driven, 300mm dia)
│   └── IHA-124 Classification Controller (Jetson Nano)
│
├── IHA-130 Sorting Mechanism
│   ├── IHA-131 Pneumatic Diverter Gates (4x)
│   ├── IHA-132 Output Chutes (4x, to each processor)
│   ├── IHA-133 Air Cylinder Assembly (SMC CDQ2)
│   └── IHA-134 Position Sensors (inductive, 4x)
│
└── IHA-140 Sensors
    ├── IHA-141 Load Cells (4x, 0-20kg each)
    ├── IHA-142 Level Sensor (ultrasonic)
    ├── IHA-143 Temperature Sensor (ambient)
    └── IHA-144 Humidity Sensor
```

### 2.3 Detailed Drawings

#### IHA-111 Main Chamber
```
                    400mm
        ┌─────────────────────────┐
        │                         │
        │    ┌───────────────┐    │
        │    │    HOPPER     │    │  400mm
   300mm│    │    OPENING    │    │  height
        │    │   250x350mm   │    │
        │    └───────┬───────┘    │
        │            │30° taper   │
        │    ┌───────┴───────┐    │
        │    │  TURNTABLE    │    │
        │    │   300mm dia   │    │
        └────┴───────────────┴────┘

Material: SS316L, 1.5mm wall
Finish: Electropolished interior
Weight: 3.2 kg
```

#### IHA-123 Turntable Assembly
```
        ┌─────────────────────┐
        │    TURNTABLE TOP    │  6mm AL6061-T6
        │     300mm dia       │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │   BEARING HOUSING   │  Sealed bearing 6205-2RS
        │                     │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │   STEPPER MOTOR     │  NEMA 23, 2.8A
        │   + PLANETARY GB    │  10:1 reduction
        └─────────────────────┘

Rotation: 0-60 RPM, bidirectional
Position accuracy: ±0.5°
Torque: 2.5 N·m continuous
```

---

## 3. Thermal Processor (TPR-200)

### 3.1 Overview
Batch pyrolysis reactor for organic waste processing at 350-450°C.

### 3.2 Components

```
TPR-200 THERMAL PROCESSOR
│
├── TPR-210 Reactor Vessel
│   ├── TPR-211 Outer Shell (SS316, 400mm dia x 350mm)
│   ├── TPR-212 Inner Liner (Inconel 625, 350mm dia)
│   ├── TPR-213 Insulation Layer (ceramic fiber, 25mm)
│   ├── TPR-214 Lid Assembly (flanged, 16 bolt)
│   └── TPR-215 Viewport (sapphire, 50mm dia)
│
├── TPR-220 Heating System
│   ├── TPR-221 Solar Thermal Receiver (parabolic focus)
│   ├── TPR-222 Electric Heater Elements (3x 1kW)
│   ├── TPR-223 Heat Pipe Assembly (sodium, 8x)
│   ├── TPR-224 Heater Controller (SSR, PID)
│   └── TPR-225 Emergency Cooling (N2 purge)
│
├── TPR-230 Gas Management
│   ├── TPR-231 Syngas Outlet (1" NPT)
│   ├── TPR-232 Condenser (shell & tube, 500W)
│   ├── TPR-233 Oil Collector (2L SS tank)
│   ├── TPR-234 Gas Scrubber (activated carbon)
│   └── TPR-235 Vacuum Pump Connection
│
├── TPR-240 Product Handling
│   ├── TPR-241 Char Collection Tray (removable)
│   ├── TPR-242 Auger Discharge (optional)
│   └── TPR-243 Cooling Jacket
│
└── TPR-250 Instrumentation
    ├── TPR-251 Thermocouples (6x Type K)
    ├── TPR-252 Pressure Transducer (0-500 kPa)
    ├── TPR-253 Gas Analyzer Port
    └── TPR-254 Mass Flow Meter (syngas)
```

### 3.3 Detailed Drawings

#### TPR-211/212 Reactor Vessel Cross-Section
```
                    ┌─────────────────────────┐
                    │      LID ASSEMBLY       │
                    │   (16x M10 bolts)       │
                    └───────────┬─────────────┘
                                │
    ┌───────────────────────────┼───────────────────────────┐
    │░░░░░░░░░░░░░░░░░░░░░░░░░░░│░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Insulation
    │░░┌─────────────────────────────────────────────────┐░░│   (25mm)
    │░░│                                                 │░░│
    │░░│        ════════════════════════════             │░░│ ← Heat pipe
    │░░│                                                 │░░│   channels (8x)
    │░░│    ┌─────────────────────────────────────┐     │░░│
    │░░│    │                                     │     │░░│
    │░░│    │         REACTION CHAMBER            │     │░░│
    │░░│    │           (Inconel 625)             │     │░░│
    │░░│    │          Volume: 30L                │     │░░│  350mm H
    │░░│    │                                     │     │░░│
    │░░│    │      Batch size: 2-5 kg             │     │░░│
    │░░│    │                                     │     │░░│
    │░░│    └───────────────────┬─────────────────┘     │░░│
    │░░│                        │                       │░░│
    │░░│        ════════════════════════════            │░░│
    │░░│                        │                       │░░│
    │░░└────────────────────────┼───────────────────────┘░░│
    │░░░░░░░░░░░░░░░░░░░░░░░░░░░│░░░░░░░░░░░░░░░░░░░░░░░░░░░│
    └───────────────────────────┼───────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │   CHAR COLLECTION     │
                    │      TRAY             │
                    └───────────────────────┘

    ├──────────────── 400mm dia ────────────────┤
```

#### TPR-221 Solar Thermal Receiver
```
    PARABOLIC CONCENTRATOR
    (deployed outside habitat)

              ╱╲
             ╱  ╲
            ╱    ╲
           ╱      ╲
          ╱   ☀    ╲
         ╱    │     ╲
        ╱     │      ╲
       ╱      ▼       ╲
      ╱───────●────────╲   ← Focus point (receiver)
     ╱                  ╲
    ╱                    ╲
   ╱______________________╲

   Diameter: 1500mm
   Focal length: 600mm
   Concentration ratio: 50:1
   Peak thermal power: 2 kW
   Material: Aluminized Mylar on carbon fiber frame
   Mass: 8 kg (deployable)

   RECEIVER DETAIL:
   ┌─────────────────┐
   │  Cavity absorber │
   │  (Inconel 625)   │  ← Absorptivity > 0.95
   │                  │
   │  ┌────────────┐  │
   │  │ Heat pipe  │──┼──→ To reactor
   │  │ interface  │  │
   │  └────────────┘  │
   └─────────────────┘
```

### 3.4 Thermal Performance

| Parameter | Value |
|-----------|-------|
| Operating temperature | 350-450°C |
| Ramp rate | 10°C/min |
| Batch size | 2-5 kg |
| Cycle time | 60-90 min |
| Heat loss | <100 W at 400°C |
| Electrical power (backup) | 800 W max |
| Solar thermal power | 1.5-2.0 kW |

---

## 4. Melt Extruder (MEX-300)

### 4.1 Overview
Single-screw extruder producing 1.75mm and 2.85mm 3D printer filament.

### 4.2 Components

```
MEX-300 MELT EXTRUDER
│
├── MEX-310 Feed System
│   ├── MEX-311 Hopper (5L, SS304)
│   ├── MEX-312 Agitator (prevents bridging)
│   ├── MEX-313 Feed Throat (water cooled)
│   └── MEX-314 Feed Screw (metering)
│
├── MEX-320 Barrel Assembly
│   ├── MEX-321 Barrel (nitrided steel, L/D=25:1)
│   ├── MEX-322 Screw (hardened, compression 3:1)
│   ├── MEX-323 Heater Bands (4 zones, 300W each)
│   ├── MEX-324 Thermocouples (4x Type J)
│   └── MEX-325 Pressure Transducer (die head)
│
├── MEX-330 Die Head
│   ├── MEX-331 Screen Pack (40/60/80 mesh)
│   ├── MEX-332 Breaker Plate
│   ├── MEX-333 Die Body (interchangeable)
│   ├── MEX-334 Die Insert 1.75mm
│   └── MEX-335 Die Insert 2.85mm
│
├── MEX-340 Downstream
│   ├── MEX-341 Water Bath (2m, temp controlled)
│   ├── MEX-342 Air Wiper
│   ├── MEX-343 Diameter Gauge (laser, ±0.01mm)
│   ├── MEX-344 Puller Rollers (servo driven)
│   └── MEX-345 Spooler (auto-wind, 1kg spool)
│
└── MEX-350 Drive System
    ├── MEX-351 Motor (1.5 kW, 3-phase)
    ├── MEX-352 Gearbox (15:1)
    ├── MEX-353 Thrust Bearing
    └── MEX-354 Coupling (flexible)
```

### 4.3 Detailed Drawings

#### MEX-320 Barrel Assembly
```
    ┌───────────────────────────────────────────────────────────────┐
    │                                                               │
    │   ZONE 1    │   ZONE 2    │   ZONE 3    │   ZONE 4    │ DIE │
    │   180°C     │   200°C     │   220°C     │   240°C     │     │
    │   (feed)    │  (compress) │   (meter)   │   (pump)    │     │
    │             │             │             │             │     │
    │  ╔═════════╤═════════════╤═════════════╤═════════════╤═════╗│
    │  ║░░░░░░░░░│░░░░░░░░░░░░░│░░░░░░░░░░░░░│░░░░░░░░░░░░░│░░░░░║│
 ───┼──╫─────────┴─────────────┴─────────────┴─────────────┴─────╫┼───→
    │  ║    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   ║│
    │  ║░░░░░░░░░│░░░░░░░░░░░░░│░░░░░░░░░░░░░│░░░░░░░░░░░░░│░░░░░║│
    │  ╚═════════╧═════════════╧═════════════╧═════════════╧═════╝│
    │      │           │           │           │           │      │
    │      TC1         TC2         TC3         TC4         P     │
    │                                                              │
    └───────────────────────────────────────────────────────────────┘

    Barrel ID: 25mm
    Barrel OD: 50mm
    Length: 625mm (L/D = 25)
    Material: Nitrided 4140 steel

    SCREW PROFILE:
    ├─ Feed section ─┤─ Compression ─┤─── Metering ───┤
         8D               8D               9D

    Compression ratio: 3:1
    Helix angle: 17.7°
    Flight depth (feed): 5mm
    Flight depth (meter): 1.7mm
```

#### MEX-343 Diameter Gauge
```
    ┌─────────────────────────────────┐
    │      LASER MICROMETER           │
    │                                 │
    │    ┌───┐           ┌───┐       │
    │    │TX │──── ⟿ ────│RX │       │
    │    │   │     │     │   │       │
    │    └───┘     ○     └───┘       │
    │           filament             │
    │                                 │
    │    Measurement range: 0.5-5mm  │
    │    Resolution: 0.001mm         │
    │    Accuracy: ±0.003mm          │
    │    Sample rate: 1000 Hz        │
    │                                 │
    └─────────────────────────────────┘
```

### 4.4 Extrusion Parameters

| Material | Zone 1 | Zone 2 | Zone 3 | Zone 4 | Die | Output |
|----------|--------|--------|--------|--------|-----|--------|
| LDPE | 160°C | 175°C | 180°C | 180°C | 175°C | 2 kg/hr |
| HDPE | 180°C | 200°C | 210°C | 210°C | 200°C | 2 kg/hr |
| PP | 190°C | 210°C | 220°C | 220°C | 210°C | 1.8 kg/hr |
| PET | 250°C | 265°C | 275°C | 275°C | 265°C | 1.5 kg/hr |

---

## 5. Mechanical Shredder (MSH-400)

### 5.1 Overview
Low-speed, high-torque shredder for foam, textiles, and composites.

### 5.2 Components

```
MSH-400 MECHANICAL SHREDDER
│
├── MSH-410 Shredder Head
│   ├── MSH-411 Cutting Chamber (hardened steel)
│   ├── MSH-412 Rotor Shaft (4140 steel, 50mm dia)
│   ├── MSH-413 Cutting Blades (D2 tool steel, 24x)
│   ├── MSH-414 Bed Knives (D2, 4x)
│   └── MSH-415 Screen (interchangeable, 5/10/20mm)
│
├── MSH-420 Drive System
│   ├── MSH-421 Motor (0.75 kW, 1750 RPM)
│   ├── MSH-422 Gearbox (50:1 worm gear)
│   ├── MSH-423 Coupling (shear pin safety)
│   └── MSH-424 Overload Protection
│
├── MSH-430 Feed System
│   ├── MSH-431 Hopper (SS304, 10L)
│   ├── MSH-432 Ram Pusher (pneumatic)
│   └── MSH-433 Feed Gate (interlocked)
│
└── MSH-440 Collection
    ├── MSH-441 Collection Bin (15L)
    ├── MSH-442 Cyclone Separator (dust)
    └── MSH-443 Bag Filter
```

### 5.3 Detailed Drawings

#### MSH-411 Cutting Chamber
```
                 FEED OPENING
                     │
    ┌────────────────┼────────────────┐
    │                ▼                │
    │    ┌───────────────────────┐    │
    │    │                       │    │
    │ ═══│═══     ═══     ═══    │═══ │ ← Bed knives
    │    │  ╲     ╱ ╲     ╱      │    │
    │    │   ╲   ╱   ╲   ╱       │    │
    │    │    ╳─────────╳        │    │ ← Rotor with blades
    │    │   ╱   ╲   ╱   ╲       │    │
    │    │  ╱     ╲ ╱     ╲      │    │
    │ ═══│═══     ═══     ═══    │═══ │
    │    │                       │    │
    │    │    ◊ ◊ ◊ ◊ ◊ ◊ ◊ ◊   │    │ ← Screen (5mm holes)
    │    │                       │    │
    │    └───────────┬───────────┘    │
    │                │                │
    └────────────────┼────────────────┘
                     ▼
              TO COLLECTION

    Chamber: 300mm x 200mm x 150mm
    Rotor: 200mm dia x 150mm long
    Blades: 24 teeth, 30mm x 30mm x 10mm
    Gap: 0.5mm blade-to-bed knife
    Speed: 35 RPM
    Torque: 200 N·m
```

---

## 6. Composite Press (CPR-500)

### 6.1 Overview
Heated hydraulic press for forming radiation shielding panels and structural composites.

### 6.2 Components

```
CPR-500 COMPOSITE PRESS
│
├── CPR-510 Press Frame
│   ├── CPR-511 Base Plate (steel, 40mm)
│   ├── CPR-512 Columns (4x, 60mm dia)
│   ├── CPR-513 Top Plate (steel, 40mm)
│   └── CPR-514 Guide Bushings (bronze)
│
├── CPR-520 Hydraulic System
│   ├── CPR-521 Cylinder (100mm bore, 150mm stroke)
│   ├── CPR-522 Pump (5L/min, 200 bar)
│   ├── CPR-523 Reservoir (10L)
│   ├── CPR-524 Valve Block (proportional)
│   └── CPR-525 Pressure Transducer
│
├── CPR-530 Heated Platens
│   ├── CPR-531 Upper Platen (300x300x30mm, AL)
│   ├── CPR-532 Lower Platen (300x300x30mm, AL)
│   ├── CPR-533 Cartridge Heaters (8x 200W)
│   ├── CPR-534 RTD Sensors (4x)
│   └── CPR-535 Cooling Channels
│
├── CPR-540 Mold System
│   ├── CPR-541 Tile Mold (300x300x50mm cavity)
│   ├── CPR-542 Rod Mold (25mm dia x 300mm)
│   ├── CPR-543 Custom Mold Adapter
│   └── CPR-544 Release Agent Applicator
│
└── CPR-550 Control
    ├── CPR-551 Press Controller
    ├── CPR-552 Safety Interlock
    └── CPR-553 Cycle Timer
```

### 6.3 Detailed Drawings

#### CPR-500 Press Assembly
```
                    ┌─────────────────────┐
                    │    HYDRAULIC        │
                    │    CYLINDER         │
                    │    (100mm bore)     │
                    └──────────┬──────────┘
                               │
    ┌──────────────────────────┼──────────────────────────┐
    │                     TOP PLATE                        │
    │                     (500x500x40)                     │
    └──────────────────────────┬──────────────────────────┘
           │                   │                   │
           │         ┌─────────┴─────────┐        │
           │         │   UPPER PLATEN    │        │
           │         │   (heated)        │        │
    ┌──────┴──┐      │   300x300x30      │      ┌─┴──────┐
    │ COLUMN  │      └─────────┬─────────┘      │ COLUMN │
    │  60mm   │                │                │  60mm  │
    │         │      ┌─────────┴─────────┐      │        │
    │         │      │      MOLD         │      │        │
    │         │      │   (300x300x50)    │      │        │
    │         │      └─────────┬─────────┘      │        │
    │         │      ┌─────────┴─────────┐      │        │
    │         │      │   LOWER PLATEN    │      │        │
    │         │      │   (heated)        │      │        │
    └──────┬──┘      │   300x300x30      │      └─┬──────┘
           │         └─────────┬─────────┘        │
    ┌──────┴───────────────────┼──────────────────┴──────┐
    │                     BASE PLATE                      │
    │                     (500x500x40)                    │
    └─────────────────────────────────────────────────────┘

    Max force: 50 tons (490 kN)
    Platen temp: ambient - 200°C
    Heating rate: 5°C/min
    Pressure control: ±1 bar
    Stroke: 0-150mm
```

### 6.4 Pressing Parameters

| Product | Temp (°C) | Pressure (MPa) | Time (min) | Cooling |
|---------|-----------|----------------|------------|---------|
| Radiation tile | 180 | 20 | 15 | Forced air |
| Structural panel | 150 | 30 | 20 | Water |
| Insulation block | 120 | 10 | 10 | Natural |

---

## 7. Control System (CTL-600)

### 7.1 Architecture

```
CTL-600 CONTROL SYSTEM
│
├── CTL-610 Main Controller
│   ├── CTL-611 Industrial PC (Intel i7, 16GB RAM)
│   ├── CTL-612 UPS (30 min backup)
│   └── CTL-613 Enclosure (IP65)
│
├── CTL-620 I/O Modules
│   ├── CTL-621 Analog Input (32 ch, 16-bit)
│   ├── CTL-622 Analog Output (8 ch, 16-bit)
│   ├── CTL-623 Digital Input (32 ch, 24V)
│   ├── CTL-624 Digital Output (32 ch, relay)
│   └── CTL-625 Thermocouple Input (16 ch)
│
├── CTL-630 Motion Control
│   ├── CTL-631 Stepper Drivers (4x)
│   ├── CTL-632 Servo Drives (2x)
│   └── CTL-633 Pneumatic Valve Bank
│
├── CTL-640 Safety System
│   ├── CTL-641 Safety PLC
│   ├── CTL-642 E-Stop Circuit
│   ├── CTL-643 Door Interlocks (4x)
│   └── CTL-644 Light Curtain
│
├── CTL-650 HMI
│   ├── CTL-651 Touchscreen (15", industrial)
│   ├── CTL-652 Indicator Lights
│   └── CTL-653 Audible Alarms
│
└── CTL-660 Communication
    ├── CTL-661 Ethernet Switch
    ├── CTL-662 WiFi AP
    └── CTL-663 RS-485 Bus
```

### 7.2 I/O Assignment

| Signal | Type | Module | Channel | Range |
|--------|------|--------|---------|-------|
| TPR Temp 1-6 | TC | CTL-625 | 1-6 | 0-600°C |
| MEX Temp 1-4 | TC | CTL-625 | 7-10 | 0-300°C |
| CPR Temp 1-4 | TC | CTL-625 | 11-14 | 0-250°C |
| Hopper Weight | AI | CTL-621 | 1-4 | 0-20 kg |
| TPR Pressure | AI | CTL-621 | 5 | 0-500 kPa |
| MEX Pressure | AI | CTL-621 | 6 | 0-50 MPa |
| CPR Pressure | AI | CTL-621 | 7 | 0-250 bar |
| Gas Flow | AI | CTL-621 | 8-10 | 0-10 L/min |
| Filament Dia | AI | CTL-621 | 11 | 0-5 mm |
| E-Stop | DI | CTL-623 | 1 | NO contact |
| Door Interlock | DI | CTL-623 | 2-5 | NC contact |
| TPR Heater 1-3 | DO | CTL-624 | 1-3 | SSR |
| MEX Heater 1-4 | DO | CTL-624 | 4-7 | SSR |
| CPR Heater 1-8 | DO | CTL-624 | 8-15 | SSR |

---

## 8. Gas Management System (GMS-700)

### 8.1 Components

```
GMS-700 GAS MANAGEMENT
│
├── GMS-710 Syngas Handling
│   ├── GMS-711 Condenser (shell & tube)
│   ├── GMS-712 Oil/Water Separator
│   ├── GMS-713 Syngas Compressor (2 bar)
│   ├── GMS-714 Storage Tank (50L, 5 bar)
│   └── GMS-715 Pressure Relief Valve
│
├── GMS-720 Scrubber System
│   ├── GMS-721 Activated Carbon Bed (10 kg)
│   ├── GMS-722 Molecular Sieve (5 kg)
│   ├── GMS-723 HEPA Filter
│   └── GMS-724 Cartridge Housing
│
├── GMS-730 Monitoring
│   ├── GMS-731 O2 Sensor (0-25%)
│   ├── GMS-732 CO Sensor (0-1000 ppm)
│   ├── GMS-733 H2 Sensor (0-4% LEL)
│   ├── GMS-734 HF Sensor (0-10 ppm)
│   └── GMS-735 CH4 Sensor (0-5% LEL)
│
└── GMS-740 Ventilation
    ├── GMS-741 Exhaust Fan (100 CFM)
    ├── GMS-742 Makeup Air Damper
    └── GMS-743 Ductwork
```

### 8.2 P&ID Diagram

```
    FROM THERMAL           FROM MELT           FROM COMPOSITE
     PROCESSOR             EXTRUDER               PRESS
         │                    │                     │
         ▼                    ▼                     ▼
    ┌─────────┐          ┌─────────┐          ┌─────────┐
    │CONDENSER│          │ FUME    │          │ FUME    │
    │ (GMS-711)          │ HOOD    │          │ HOOD    │
    └────┬────┘          └────┬────┘          └────┬────┘
         │                    │                     │
         │    ┌───────────────┴─────────────────────┘
         │    │
         ▼    ▼
    ┌──────────────┐
    │  OIL/WATER   │───→ Oil Collection
    │  SEPARATOR   │───→ Water Recovery
    │  (GMS-712)   │
    └──────┬───────┘
           │ (clean gas)
           ▼
    ┌──────────────┐
    │  ACTIVATED   │
    │   CARBON     │
    │  (GMS-721)   │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  MOLECULAR   │
    │    SIEVE     │
    │  (GMS-722)   │
    └──────┬───────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌───────┐    ┌───────────┐
│STORAGE│    │  HABITAT  │
│ TANK  │    │   RETURN  │
│(syngas│    │  (clean)  │
└───────┘    └───────────┘
```

---

## 9. Assembly Sequence

### 9.1 Phase 1: Base Frame Assembly
1. Level base frame on floor
2. Install leveling feet, adjust to ±0.5mm
3. Verify frame squareness (diagonal check)
4. Secure all frame bolts to torque spec

### 9.2 Phase 2: Module Installation
1. Install control cabinet on frame
2. Position thermal processor, secure with bolts
3. Install melt extruder, align with thermal outlet
4. Mount mechanical shredder
5. Install composite press
6. Mount input hopper assembly
7. Install gas management system

### 9.3 Phase 3: Interconnections
1. Install conveyors/chutes between modules
2. Connect gas ducting
3. Install cooling water piping
4. Route electrical conduits
5. Install pneumatic tubing

### 9.4 Phase 4: Electrical
1. Install main power distribution
2. Wire I/O modules to sensors/actuators
3. Connect heater power circuits
4. Install motor power cables
5. Verify grounding continuity
6. Megger test all circuits

### 9.5 Phase 5: Commissioning
1. Power-on test (no heat)
2. I/O verification
3. Motion checkout
4. Heating system calibration
5. Safety system verification
6. Process integration test

---

## 10. Drawing Index

| Drawing No. | Title | Rev |
|-------------|-------|-----|
| ARTEMIS-001 | System Assembly | A |
| ARTEMIS-100 | Input Hopper Assembly | A |
| ARTEMIS-200 | Thermal Processor Assembly | A |
| ARTEMIS-300 | Melt Extruder Assembly | A |
| ARTEMIS-400 | Mechanical Shredder Assembly | A |
| ARTEMIS-500 | Composite Press Assembly | A |
| ARTEMIS-600 | Control System Layout | A |
| ARTEMIS-700 | Gas Management P&ID | A |
| ARTEMIS-800 | Electrical Schematics | A |
| ARTEMIS-900 | Solar Concentrator Assembly | A |

---

*Document Version: 1.0*
*Format: ASCII CAD (SolidWorks/Fusion360 files available)*
