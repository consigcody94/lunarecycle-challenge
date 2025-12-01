"""
ARTEMIS-R Processing Modules

Physical simulation models matching the CAD specifications for each
processing module in the ARTEMIS-R system.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
import math

from lunarecycle.waste.streams import WasteItem, WasteCategory
from lunarecycle.waste.materials import Material, MaterialType
from lunarecycle.recycling.processes import (
    ProcessingResult,
    Product,
    ProductType,
    RecyclingProcess,
)


class ModuleState(Enum):
    """Operational state of a processing module."""

    IDLE = auto()
    HEATING = auto()
    PROCESSING = auto()
    COOLING = auto()
    ERROR = auto()
    MAINTENANCE = auto()


@dataclass
class ThermalState:
    """Thermal state of a module."""

    current_temp_c: float = 25.0
    target_temp_c: float = 25.0
    heating_rate_c_per_min: float = 10.0
    cooling_rate_c_per_min: float = 5.0
    solar_power_available: bool = False
    electrical_power_w: float = 0.0


@dataclass
class SensorReadings:
    """Sensor data from a module."""

    temperatures: dict[str, float] = field(default_factory=dict)
    pressures: dict[str, float] = field(default_factory=dict)
    mass_kg: float = 0.0
    gas_composition: dict[str, float] = field(default_factory=dict)
    energy_consumed_kwh: float = 0.0


class InputHopper:
    """
    IHA-100 Input Hopper Assembly

    AI-assisted waste classification and sorting system.
    Specifications:
    - Capacity: 20 kg
    - Turntable: 300mm diameter
    - Classification accuracy: 95%+
    - 4 output chutes to processing modules
    """

    def __init__(self):
        self.capacity_kg = 20.0
        self.current_load_kg = 0.0
        self.state = ModuleState.IDLE
        self.turntable_position_deg = 0.0
        self.classification_accuracy = 0.95

        # Material bins
        self.bins: dict[str, list[tuple[WasteItem, float]]] = {
            "thermal": [],  # Organic waste for pyrolysis
            "melt": [],  # Thermoplastics for extrusion
            "shredder": [],  # Foam, textiles for mechanical processing
            "press": [],  # Ready for composite pressing
        }

    def add_waste(self, items: list[WasteItem], masses: list[float]) -> dict[str, int]:
        """
        Add waste items and classify them for routing.

        Returns dict of item counts per destination.
        """
        routing = {"thermal": 0, "melt": 0, "shredder": 0, "press": 0}

        for item, mass in zip(items, masses):
            destination = self._classify(item)
            self.bins[destination].append((item, mass))
            routing[destination] += 1
            self.current_load_kg += mass

        return routing

    def _classify(self, item: WasteItem) -> str:
        """Classify waste item and determine destination module."""
        # Foam goes to shredder (never thermal - PVDF safety)
        if item.category == WasteCategory.FOAM_PACKING:
            return "shredder"

        # Thermoplastics go to melt extruder
        if item.composition.primary_material in {"LDPE", "HDPE", "PP", "PET", "PE"}:
            return "melt"

        # Textiles go to shredder first
        if item.category == WasteCategory.CLOTHING:
            if item.composition.primary_material in {"Cotton", "COTTON"}:
                return "shredder"  # Natural fibers for composite
            return "melt"  # Synthetic fibers can be melted

        # Paper, hygiene, food packaging remnants go to thermal
        if item.category in {
            WasteCategory.FOOD_PACKAGING,
            WasteCategory.HYGIENE_ITEMS,
            WasteCategory.GENERAL_WASTE,
        }:
            return "thermal"

        # Default to thermal processing
        return "thermal"

    def get_batch(self, destination: str, max_mass: float) -> list[tuple[WasteItem, float]]:
        """Get a batch of items for a destination module."""
        batch = []
        batch_mass = 0.0

        while self.bins[destination] and batch_mass < max_mass:
            item, mass = self.bins[destination][0]
            if batch_mass + mass <= max_mass:
                batch.append((item, mass))
                batch_mass += mass
                self.bins[destination].pop(0)
                self.current_load_kg -= mass
            else:
                break

        return batch

    def get_status(self) -> dict:
        """Get current hopper status."""
        return {
            "state": self.state.name,
            "load_kg": self.current_load_kg,
            "capacity_kg": self.capacity_kg,
            "fill_percent": (self.current_load_kg / self.capacity_kg) * 100,
            "bins": {name: len(items) for name, items in self.bins.items()},
        }


class ThermalProcessor(RecyclingProcess):
    """
    TPR-200 Thermal Processor (Solar-Assisted Pyrolysis)

    Specifications:
    - Reactor volume: 30L
    - Operating temperature: 350-450°C
    - Batch size: 2-5 kg
    - Cycle time: 60-90 minutes
    - Heating: Solar thermal (1.5-2.0 kW) + Electric backup (800W)
    """

    def __init__(
        self,
        operating_temp_c: float = 400.0,
        solar_available: bool = True,
    ):
        super().__init__("ARTEMIS Thermal Processor", max_capacity_kg_hr=3.0)
        self.operating_temp_c = operating_temp_c
        self.solar_available = solar_available
        self.reactor_volume_l = 30.0
        self.batch_capacity_kg = 5.0

        # Energy parameters
        self.solar_power_kw = 1.8 if solar_available else 0.0
        self.electric_power_kw = 0.8
        self.specific_heat_capacity = 1.2  # kWh/kg to heat to operating temp

        # State
        self.state = ModuleState.IDLE
        self.thermal = ThermalState(target_temp_c=operating_temp_c)
        self.current_batch: list[tuple[WasteItem, float]] = []

    def can_process(self, waste_item: WasteItem) -> bool:
        """Check if item is safe for thermal processing."""
        # CRITICAL: Never process PVDF in thermal zone
        if "PVDF" in waste_item.composition.primary_material:
            return False
        if "F" in str(waste_item.composition.secondary_materials):
            return False

        # Accept organic materials
        return waste_item.category in {
            WasteCategory.FOOD_PACKAGING,
            WasteCategory.CLOTHING,
            WasteCategory.HYGIENE_ITEMS,
            WasteCategory.GENERAL_WASTE,
            WasteCategory.SCIENCE_MATERIALS,
        }

    def get_energy_requirement(self, mass_kg: float) -> float:
        """Calculate energy requirement accounting for solar contribution."""
        total_energy = mass_kg * self.specific_heat_capacity

        if self.solar_available:
            # Solar provides ~70% of thermal energy
            electrical = total_energy * 0.3
        else:
            electrical = total_energy

        return electrical

    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """Process waste through solar-assisted pyrolysis."""
        total_input = sum(masses_kg)

        # Filter out unsafe items
        safe_items = []
        safe_masses = []
        rejected_mass = 0.0

        for item, mass in zip(waste_items, masses_kg):
            if self.can_process(item):
                safe_items.append(item)
                safe_masses.append(mass)
            else:
                rejected_mass += mass

        processable_mass = sum(safe_masses)

        # Calculate pyrolysis yields
        syngas_mass = 0.0
        oil_mass = 0.0
        char_mass = 0.0
        water_mass = 0.0
        metal_mass = 0.0
        energy_content_mj = 0.0

        for item, mass in zip(safe_items, safe_masses):
            mat = Material.get_by_name(item.composition.primary_material)
            if mat:
                syngas_mass += mass * (mat.pyrolysis.syngas_yield_percent / 100)
                oil_mass += mass * (mat.pyrolysis.oil_yield_percent / 100)
                char_mass += mass * (mat.pyrolysis.char_yield_percent / 100)
                water_mass += mass * (mat.pyrolysis.water_yield_percent / 100)
                energy_content_mj += mass * mat.heating_value_mj_kg * 0.65
            else:
                # Default yields
                syngas_mass += mass * 0.25
                oil_mass += mass * 0.45
                char_mass += mass * 0.20
                water_mass += mass * 0.10

            # Metal recovery from multi-layer packaging
            if "Aluminum" in item.composition.secondary_materials:
                al_frac = item.composition.secondary_materials["Aluminum"] / 100
                metal_mass += mass * al_frac

        # Build products
        products = []
        if syngas_mass > 0.001:
            products.append(
                Product(
                    product_type=ProductType.SYNGAS,
                    mass_kg=syngas_mass,
                    quality_score=0.88,
                    energy_content_mj=energy_content_mj * 0.4,
                    description="Synthesis gas (H2 40%, CO 35%, CH4 20%)",
                )
            )
        if oil_mass > 0.001:
            products.append(
                Product(
                    product_type=ProductType.PYROLYSIS_OIL,
                    mass_kg=oil_mass,
                    quality_score=0.75,
                    energy_content_mj=energy_content_mj * 0.5,
                    description="Pyrolysis oil - feedstock grade",
                )
            )
        if char_mass > 0.001:
            products.append(
                Product(
                    product_type=ProductType.CHAR,
                    mass_kg=char_mass,
                    quality_score=0.92,
                    energy_content_mj=energy_content_mj * 0.1,
                    description="Biochar - composite filler grade",
                )
            )
        if water_mass > 0.001:
            products.append(
                Product(
                    product_type=ProductType.WATER,
                    mass_kg=water_mass,
                    quality_score=0.55,
                    description="Condensate water - requires treatment",
                )
            )
        if metal_mass > 0.001:
            products.append(
                Product(
                    product_type=ProductType.METAL,
                    mass_kg=metal_mass,
                    quality_score=0.90,
                    description="Recovered aluminum",
                )
            )

        product_mass = sum(p.mass_kg for p in products)
        processing_time = 1.0 + (processable_mass / 5.0)  # Base 1hr + mass factor

        return ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=products,
            waste_residue_kg=rejected_mass + max(0, processable_mass - product_mass),
            mass_recovery_rate=product_mass / processable_mass if processable_mass > 0 else 0,
            energy_consumed_kwh=self.get_energy_requirement(processable_mass),
            energy_recovered_kwh=energy_content_mj / 3.6,
            processing_time_hours=processing_time,
            toxins_released=False,
            microplastics_generated=False,
        )

    def get_status(self) -> dict:
        """Get current processor status."""
        return {
            "state": self.state.name,
            "temperature_c": self.thermal.current_temp_c,
            "target_temp_c": self.thermal.target_temp_c,
            "solar_available": self.solar_available,
            "batch_items": len(self.current_batch),
        }


class MeltExtruder(RecyclingProcess):
    """
    MEX-300 Melt Extruder

    Specifications:
    - Barrel: 25mm x 625mm (L/D=25)
    - Output: 1.75mm or 2.85mm filament
    - Temperature zones: 4 (180-280°C)
    - Throughput: 2 kg/hr
    - Power: 1.2 kW continuous
    """

    def __init__(
        self,
        output_diameter_mm: float = 1.75,
    ):
        super().__init__("ARTEMIS Melt Extruder", max_capacity_kg_hr=2.0)
        self.output_diameter = output_diameter_mm
        self.barrel_diameter_mm = 25.0
        self.barrel_length_mm = 625.0
        self.ld_ratio = 25.0

        # Temperature zones
        self.zone_temps = {
            "zone1_feed": 180.0,
            "zone2_compress": 200.0,
            "zone3_meter": 220.0,
            "zone4_pump": 240.0,
            "die": 230.0,
        }

        # State
        self.state = ModuleState.IDLE
        self.screw_rpm = 0.0
        self.melt_pressure_bar = 0.0

        # Acceptable materials
        self.thermoplastics = {"LDPE", "HDPE", "PP", "PET", "PE", "POLYESTER", "NYLON"}

    def can_process(self, waste_item: WasteItem) -> bool:
        """Check if item is a melt-processable thermoplastic."""
        return waste_item.composition.primary_material.upper() in self.thermoplastics

    def get_energy_requirement(self, mass_kg: float) -> float:
        """Energy for melt extrusion."""
        return mass_kg * 0.6  # 0.6 kWh/kg typical for extrusion

    def set_temperatures(self, material: str) -> None:
        """Set zone temperatures for material type."""
        profiles = {
            "LDPE": [160, 175, 180, 180, 175],
            "HDPE": [180, 200, 210, 210, 200],
            "PP": [190, 210, 220, 220, 210],
            "PET": [250, 265, 275, 275, 265],
        }
        temps = profiles.get(material.upper(), profiles["LDPE"])
        self.zone_temps = {
            "zone1_feed": temps[0],
            "zone2_compress": temps[1],
            "zone3_meter": temps[2],
            "zone4_pump": temps[3],
            "die": temps[4],
        }

    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """Extrude thermoplastics into filament."""
        total_input = sum(masses_kg)
        processable_mass = 0.0
        rejected_mass = 0.0

        for item, mass in zip(waste_items, masses_kg):
            if self.can_process(item):
                processable_mass += mass
            else:
                rejected_mass += mass

        # Extrusion efficiency (material loss from die, trim, etc.)
        efficiency = 0.94
        filament_mass = processable_mass * efficiency

        products = []
        if filament_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.FILAMENT,
                    mass_kg=filament_mass,
                    quality_score=0.82,
                    description=f"Recycled filament {self.output_diameter}mm",
                )
            )

        processing_time = processable_mass / self.max_capacity_kg_hr

        return ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=products,
            waste_residue_kg=rejected_mass + (processable_mass - filament_mass),
            mass_recovery_rate=filament_mass / processable_mass if processable_mass > 0 else 0,
            energy_consumed_kwh=self.get_energy_requirement(processable_mass),
            processing_time_hours=processing_time,
            microplastics_generated=True,  # Some particles during shredding
        )

    def get_filament_quality(self, target_diameter: float, actual_diameter: float) -> float:
        """Calculate quality score based on diameter tolerance."""
        tolerance = abs(actual_diameter - target_diameter)
        if tolerance <= 0.02:
            return 1.0
        elif tolerance <= 0.05:
            return 0.9
        elif tolerance <= 0.10:
            return 0.7
        else:
            return 0.5

    def get_status(self) -> dict:
        """Get current extruder status."""
        return {
            "state": self.state.name,
            "screw_rpm": self.screw_rpm,
            "melt_pressure_bar": self.melt_pressure_bar,
            "zone_temps": self.zone_temps,
            "output_diameter_mm": self.output_diameter,
        }


class MechanicalShredder(RecyclingProcess):
    """
    MSH-400 Mechanical Shredder

    Specifications:
    - Rotor: 200mm dia x 150mm
    - Speed: 35 RPM (high torque)
    - Screen sizes: 5/10/20mm
    - Throughput: 5 kg/hr
    - Power: 0.75 kW
    """

    def __init__(self, screen_size_mm: float = 5.0):
        super().__init__("ARTEMIS Mechanical Shredder", max_capacity_kg_hr=5.0)
        self.screen_size_mm = screen_size_mm
        self.rotor_rpm = 35.0
        self.rotor_diameter_mm = 200.0

        # State
        self.state = ModuleState.IDLE
        self.motor_current_a = 0.0
        self.jam_detected = False

    def can_process(self, waste_item: WasteItem) -> bool:
        """Shredder can process foam, textiles, and most materials."""
        # Don't shred metals or very hard materials
        mat = Material.get_by_name(waste_item.composition.primary_material)
        if mat and mat.material_type == MaterialType.METAL:
            return False
        return True

    def get_energy_requirement(self, mass_kg: float) -> float:
        """Energy for mechanical shredding."""
        return mass_kg * 0.15  # Very efficient mechanical process

    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """Shred materials into particles."""
        total_input = sum(masses_kg)

        # Separate foam and fiber for different handling
        foam_mass = 0.0
        fiber_mass = 0.0
        other_mass = 0.0

        for item, mass in zip(waste_items, masses_kg):
            if item.category == WasteCategory.FOAM_PACKING:
                foam_mass += mass
            elif item.category == WasteCategory.CLOTHING:
                fiber_mass += mass
            else:
                other_mass += mass

        # Products
        products = []

        # Shredded foam particles (lightweight filler)
        if foam_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.COMPOSITE,
                    mass_kg=foam_mass * 0.98,  # Minimal loss
                    quality_score=0.90,
                    description=f"Foam particles <{self.screen_size_mm}mm - radiation shield filler",
                )
            )

        # Defibrated textile
        if fiber_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.COMPOSITE,
                    mass_kg=fiber_mass * 0.95,
                    quality_score=0.85,
                    description="Defibrated textile - reinforcement fiber",
                )
            )

        # Other shredded material
        if other_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.COMPOSITE,
                    mass_kg=other_mass * 0.92,
                    quality_score=0.75,
                    description="Shredded material - composite filler",
                )
            )

        product_mass = sum(p.mass_kg for p in products)
        processing_time = total_input / self.max_capacity_kg_hr

        return ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=products,
            waste_residue_kg=total_input - product_mass,
            mass_recovery_rate=product_mass / total_input if total_input > 0 else 0,
            energy_consumed_kwh=self.get_energy_requirement(total_input),
            processing_time_hours=processing_time,
            microplastics_generated=True,  # Dust generated
        )

    def get_status(self) -> dict:
        """Get current shredder status."""
        return {
            "state": self.state.name,
            "rotor_rpm": self.rotor_rpm,
            "motor_current_a": self.motor_current_a,
            "screen_size_mm": self.screen_size_mm,
            "jam_detected": self.jam_detected,
        }


class CompositePress(RecyclingProcess):
    """
    CPR-500 Composite Press

    Specifications:
    - Platen size: 300x300mm
    - Max force: 50 tons (490 kN)
    - Temperature: up to 200°C
    - Stroke: 150mm
    - Products: 300x300x50mm tiles
    """

    def __init__(
        self,
        platen_temp_c: float = 180.0,
        pressing_pressure_mpa: float = 20.0,
    ):
        super().__init__("ARTEMIS Composite Press", max_capacity_kg_hr=3.0)
        self.platen_temp_c = platen_temp_c
        self.pressing_pressure_mpa = pressing_pressure_mpa
        self.platen_size_mm = 300.0
        self.max_force_kn = 490.0

        # State
        self.state = ModuleState.IDLE
        self.current_temp_c = 25.0
        self.current_pressure_mpa = 0.0

        # Mold dimensions
        self.tile_dimensions_mm = (300, 300, 50)  # L x W x H

    def can_process(self, waste_item: WasteItem) -> bool:
        """Press accepts pre-processed composite materials."""
        return True  # Accepts mixed shredded/char materials

    def get_energy_requirement(self, mass_kg: float) -> float:
        """Energy for heated pressing."""
        return mass_kg * 0.3  # Heating + hydraulics

    def calculate_tile_properties(
        self,
        foam_fraction: float,
        char_fraction: float,
        regolith_fraction: float,
        binder_fraction: float,
    ) -> dict:
        """Calculate composite tile properties based on composition."""
        # Density calculation
        densities = {
            "foam": 30,  # kg/m³
            "char": 500,
            "regolith": 1500,
            "binder": 950,
        }
        composite_density = (
            foam_fraction * densities["foam"]
            + char_fraction * densities["char"]
            + regolith_fraction * densities["regolith"]
            + binder_fraction * densities["binder"]
        )

        # Hydrogen content for radiation shielding
        # Foam and binder contribute H, regolith minimal
        h_content = foam_fraction * 0.08 + binder_fraction * 0.14

        # Radiation attenuation (% per 10cm for GCR)
        # Higher H content = better shielding
        gcr_attenuation = 10 + h_content * 150  # 10-25% range

        # Compressive strength (MPa)
        # Higher regolith and char = stronger
        strength = 10 + regolith_fraction * 40 + char_fraction * 20

        # Thermal conductivity (W/m·K)
        # Foam = insulator, regolith = conductor
        thermal_k = foam_fraction * 0.03 + regolith_fraction * 0.8 + char_fraction * 0.15 + binder_fraction * 0.2

        return {
            "density_kg_m3": composite_density,
            "hydrogen_content_percent": h_content * 100,
            "gcr_attenuation_percent_10cm": gcr_attenuation,
            "compressive_strength_mpa": strength,
            "thermal_conductivity_w_mk": thermal_k,
        }

    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """Press materials into composite tiles."""
        total_input = sum(masses_kg)

        # Calculate composition
        foam_mass = 0.0
        char_mass = 0.0
        fiber_mass = 0.0
        other_mass = 0.0

        for item, mass in zip(waste_items, masses_kg):
            if item.category == WasteCategory.FOAM_PACKING:
                foam_mass += mass
            elif "char" in item.name.lower() or "biochar" in item.name.lower():
                char_mass += mass
            elif item.category == WasteCategory.CLOTHING:
                fiber_mass += mass
            else:
                other_mass += mass

        # Assume 10% thermoplastic binder added (not from waste)
        binder_added = total_input * 0.10

        # Calculate fractions
        total_with_binder = total_input + binder_added
        foam_frac = foam_mass / total_with_binder if total_with_binder > 0 else 0
        char_frac = char_mass / total_with_binder if total_with_binder > 0 else 0
        binder_frac = binder_added / total_with_binder if total_with_binder > 0 else 0

        # Add regolith simulant (20% of composite)
        regolith_frac = 0.20
        adjusted_total = total_with_binder / (1 - regolith_frac)
        regolith_mass = adjusted_total * regolith_frac

        # Calculate properties
        props = self.calculate_tile_properties(
            foam_fraction=foam_frac * 0.8,
            char_fraction=char_frac * 0.8,
            regolith_fraction=regolith_frac,
            binder_fraction=binder_frac * 0.8,
        )

        # Pressing efficiency
        efficiency = 0.96
        tile_mass = (total_input + regolith_mass) * efficiency

        # Number of tiles produced
        tile_volume_m3 = (0.3 * 0.3 * 0.05)  # 300x300x50mm in m³
        tile_mass_each = props["density_kg_m3"] * tile_volume_m3
        num_tiles = int(tile_mass / tile_mass_each) if tile_mass_each > 0 else 0

        products = []
        if tile_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.COMPOSITE,
                    mass_kg=tile_mass,
                    quality_score=0.88,
                    description=f"Radiation shielding tiles ({num_tiles}x) - {props['gcr_attenuation_percent_10cm']:.1f}% GCR attenuation",
                )
            )

        processing_time = 0.25 + (num_tiles * 0.25)  # 15 min setup + 15 min per tile

        return ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=products,
            waste_residue_kg=(total_input + regolith_mass) - tile_mass,
            mass_recovery_rate=tile_mass / (total_input + regolith_mass) if total_input > 0 else 0,
            energy_consumed_kwh=self.get_energy_requirement(tile_mass),
            processing_time_hours=processing_time,
        )

    def get_status(self) -> dict:
        """Get current press status."""
        return {
            "state": self.state.name,
            "platen_temp_c": self.current_temp_c,
            "target_temp_c": self.platen_temp_c,
            "pressure_mpa": self.current_pressure_mpa,
            "platen_size_mm": self.platen_size_mm,
        }
