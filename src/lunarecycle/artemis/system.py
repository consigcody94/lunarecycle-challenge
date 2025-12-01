"""
ARTEMIS-R Integrated System

Main system class that coordinates all processing modules
and manages material flow through the recycling pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import json

from lunarecycle.waste.streams import WasteItem, WasteStream, WasteCategory
from lunarecycle.waste.inventory import WasteInventory
from lunarecycle.recycling.processes import ProcessingResult, Product, ProductType
from .modules import (
    InputHopper,
    ThermalProcessor,
    MeltExtruder,
    MechanicalShredder,
    CompositePress,
    ModuleState,
)


@dataclass
class SystemMetrics:
    """Aggregated metrics for the ARTEMIS-R system."""

    total_waste_input_kg: float = 0.0
    total_products_kg: float = 0.0
    total_residue_kg: float = 0.0
    total_energy_consumed_kwh: float = 0.0
    total_energy_recovered_kwh: float = 0.0
    total_processing_hours: float = 0.0

    # Product breakdown
    syngas_produced_kg: float = 0.0
    oil_produced_kg: float = 0.0
    char_produced_kg: float = 0.0
    filament_produced_kg: float = 0.0
    tiles_produced_kg: float = 0.0
    water_recovered_kg: float = 0.0
    metal_recovered_kg: float = 0.0

    # Efficiency metrics
    processing_runs: int = 0

    @property
    def mass_recovery_rate(self) -> float:
        if self.total_waste_input_kg > 0:
            return self.total_products_kg / self.total_waste_input_kg
        return 0.0

    @property
    def net_energy_kwh(self) -> float:
        return self.total_energy_recovered_kwh - self.total_energy_consumed_kwh

    @property
    def energy_efficiency(self) -> float:
        if self.total_energy_consumed_kwh > 0:
            return self.total_energy_recovered_kwh / self.total_energy_consumed_kwh
        return 0.0


@dataclass
class ProcessingEvent:
    """Record of a processing event."""

    timestamp: datetime
    module: str
    input_mass_kg: float
    output_mass_kg: float
    energy_kwh: float
    products: list[dict]
    duration_hours: float


class ARTEMISSystem:
    """
    ARTEMIS-R Integrated Recycling System

    Coordinates material flow between:
    - Input Hopper (IHA-100): Sorting and classification
    - Thermal Processor (TPR-200): Pyrolysis
    - Melt Extruder (MEX-300): Filament production
    - Mechanical Shredder (MSH-400): Size reduction
    - Composite Press (CPR-500): Tile fabrication
    """

    def __init__(
        self,
        solar_available: bool = True,
        regolith_available: bool = True,
    ):
        # Initialize modules
        self.hopper = InputHopper()
        self.thermal = ThermalProcessor(solar_available=solar_available)
        self.extruder = MeltExtruder(output_diameter_mm=1.75)
        self.shredder = MechanicalShredder(screen_size_mm=5.0)
        self.press = CompositePress(platen_temp_c=180.0)

        # System configuration
        self.solar_available = solar_available
        self.regolith_available = regolith_available

        # Intermediate storage (between modules)
        self.char_storage_kg: float = 0.0
        self.foam_particles_kg: float = 0.0
        self.fiber_storage_kg: float = 0.0

        # Metrics
        self.metrics = SystemMetrics()
        self.processing_history: list[ProcessingEvent] = []

        # System state
        self.current_time = datetime.now()
        self.operating = False

    def start(self) -> None:
        """Start the system."""
        self.operating = True
        for module in [self.thermal, self.extruder, self.shredder, self.press]:
            module.state = ModuleState.IDLE

    def stop(self) -> None:
        """Stop the system."""
        self.operating = False

    def add_waste(self, items: list[WasteItem], masses: list[float]) -> dict:
        """Add waste to the input hopper for processing."""
        return self.hopper.add_waste(items, masses)

    def process_thermal_batch(self) -> Optional[ProcessingResult]:
        """Process a batch through the thermal processor."""
        batch = self.hopper.get_batch("thermal", self.thermal.batch_capacity_kg)
        if not batch:
            return None

        items = [item for item, mass in batch]
        masses = [mass for item, mass in batch]

        result = self.thermal.process(items, masses)
        self._record_event("thermal", result)

        # Store char for composite fabrication
        for product in result.products:
            if product.product_type == ProductType.CHAR:
                self.char_storage_kg += product.mass_kg

        return result

    def process_extrusion_batch(self) -> Optional[ProcessingResult]:
        """Process a batch through the melt extruder."""
        batch = self.hopper.get_batch("melt", 5.0)  # 5kg max batch
        if not batch:
            return None

        items = [item for item, mass in batch]
        masses = [mass for item, mass in batch]

        result = self.extruder.process(items, masses)
        self._record_event("extruder", result)

        return result

    def process_shredder_batch(self) -> Optional[ProcessingResult]:
        """Process a batch through the mechanical shredder."""
        batch = self.hopper.get_batch("shredder", 10.0)  # 10kg max batch
        if not batch:
            return None

        items = [item for item, mass in batch]
        masses = [mass for item, mass in batch]

        result = self.shredder.process(items, masses)
        self._record_event("shredder", result)

        # Store shredded materials for composite
        for product in result.products:
            if "foam" in product.description.lower():
                self.foam_particles_kg += product.mass_kg
            elif "fiber" in product.description.lower():
                self.fiber_storage_kg += product.mass_kg

        return result

    def process_composite_batch(self) -> Optional[ProcessingResult]:
        """Combine stored materials in composite press."""
        # Need minimum materials for a batch
        min_batch = 2.0  # kg

        available = self.char_storage_kg + self.foam_particles_kg + self.fiber_storage_kg
        if available < min_batch:
            return None

        # Create synthetic waste items for tracking
        items = []
        masses = []

        # Create simple tracking objects for composite ingredients
        # These are intermediate products, not original waste items
        from lunarecycle.waste.streams import MaterialComposition, DifficultyLevel

        if self.char_storage_kg > 0:
            char_item = WasteItem(
                name="Biochar",
                category=WasteCategory.GENERAL_WASTE,
                difficulty=DifficultyLevel.LEVEL_1,
                mass_per_unit_kg=1.0,
                volume_per_unit_m3=0.002,
                density_kg_m3=500.0,
                generation_rate_per_crew_day=0.0,
                composition=MaterialComposition("Carbon", 100.0),
            )
            items.append(char_item)
            masses.append(self.char_storage_kg)

        if self.foam_particles_kg > 0:
            foam_item = WasteItem(
                name="Foam Particles",
                category=WasteCategory.FOAM_PACKING,
                difficulty=DifficultyLevel.LEVEL_3,
                mass_per_unit_kg=1.0,
                volume_per_unit_m3=0.033,
                density_kg_m3=30.0,
                generation_rate_per_crew_day=0.0,
                composition=MaterialComposition("PVDF", 100.0),
            )
            items.append(foam_item)
            masses.append(self.foam_particles_kg)

        if self.fiber_storage_kg > 0:
            fiber_item = WasteItem(
                name="Textile Fiber",
                category=WasteCategory.CLOTHING,
                difficulty=DifficultyLevel.LEVEL_2,
                mass_per_unit_kg=1.0,
                volume_per_unit_m3=0.005,
                density_kg_m3=200.0,
                generation_rate_per_crew_day=0.0,
                composition=MaterialComposition("Cotton", 100.0),
            )
            items.append(fiber_item)
            masses.append(self.fiber_storage_kg)

        result = self.press.process(items, masses)
        self._record_event("press", result)

        # Clear storage
        self.char_storage_kg = 0.0
        self.foam_particles_kg = 0.0
        self.fiber_storage_kg = 0.0

        return result

    def process_all(self) -> dict[str, ProcessingResult]:
        """Process all available waste through appropriate modules."""
        results = {}

        # Process in optimal order
        thermal_result = self.process_thermal_batch()
        if thermal_result:
            results["thermal"] = thermal_result

        extrusion_result = self.process_extrusion_batch()
        if extrusion_result:
            results["extruder"] = extrusion_result

        shredder_result = self.process_shredder_batch()
        if shredder_result:
            results["shredder"] = shredder_result

        # Composite pressing last (uses outputs from other modules)
        composite_result = self.process_composite_batch()
        if composite_result:
            results["press"] = composite_result

        return results

    def _record_event(self, module: str, result: ProcessingResult) -> None:
        """Record processing event and update metrics."""
        event = ProcessingEvent(
            timestamp=self.current_time,
            module=module,
            input_mass_kg=result.input_mass_kg,
            output_mass_kg=result.total_product_mass,
            energy_kwh=result.energy_consumed_kwh,
            products=[
                {"type": p.product_type.name, "mass_kg": p.mass_kg, "quality": p.quality_score}
                for p in result.products
            ],
            duration_hours=result.processing_time_hours,
        )
        self.processing_history.append(event)

        # Update metrics
        self.metrics.total_waste_input_kg += result.input_mass_kg
        self.metrics.total_products_kg += result.total_product_mass
        self.metrics.total_residue_kg += result.waste_residue_kg
        self.metrics.total_energy_consumed_kwh += result.energy_consumed_kwh
        self.metrics.total_energy_recovered_kwh += result.energy_recovered_kwh
        self.metrics.total_processing_hours += result.processing_time_hours
        self.metrics.processing_runs += 1

        # Update product breakdown
        for product in result.products:
            if product.product_type == ProductType.SYNGAS:
                self.metrics.syngas_produced_kg += product.mass_kg
            elif product.product_type == ProductType.PYROLYSIS_OIL:
                self.metrics.oil_produced_kg += product.mass_kg
            elif product.product_type == ProductType.CHAR:
                self.metrics.char_produced_kg += product.mass_kg
            elif product.product_type == ProductType.FILAMENT:
                self.metrics.filament_produced_kg += product.mass_kg
            elif product.product_type == ProductType.COMPOSITE:
                self.metrics.tiles_produced_kg += product.mass_kg
            elif product.product_type == ProductType.WATER:
                self.metrics.water_recovered_kg += product.mass_kg
            elif product.product_type == ProductType.METAL:
                self.metrics.metal_recovered_kg += product.mass_kg

        # Advance time
        self.current_time += timedelta(hours=result.processing_time_hours)

    def get_status(self) -> dict:
        """Get comprehensive system status."""
        return {
            "operating": self.operating,
            "current_time": self.current_time.isoformat(),
            "solar_available": self.solar_available,
            "modules": {
                "hopper": self.hopper.get_status(),
                "thermal": self.thermal.get_status(),
                "extruder": self.extruder.get_status(),
                "shredder": self.shredder.get_status(),
                "press": self.press.get_status(),
            },
            "storage": {
                "char_kg": self.char_storage_kg,
                "foam_particles_kg": self.foam_particles_kg,
                "fiber_kg": self.fiber_storage_kg,
            },
            "metrics": {
                "total_input_kg": self.metrics.total_waste_input_kg,
                "total_products_kg": self.metrics.total_products_kg,
                "mass_recovery_rate": self.metrics.mass_recovery_rate,
                "net_energy_kwh": self.metrics.net_energy_kwh,
                "processing_runs": self.metrics.processing_runs,
            },
        }

    def get_product_summary(self) -> dict:
        """Get summary of all products produced."""
        return {
            "syngas_kg": self.metrics.syngas_produced_kg,
            "pyrolysis_oil_kg": self.metrics.oil_produced_kg,
            "biochar_kg": self.metrics.char_produced_kg,
            "filament_kg": self.metrics.filament_produced_kg,
            "composite_tiles_kg": self.metrics.tiles_produced_kg,
            "water_kg": self.metrics.water_recovered_kg,
            "metal_kg": self.metrics.metal_recovered_kg,
            "total_kg": self.metrics.total_products_kg,
        }

    def get_energy_summary(self) -> dict:
        """Get energy balance summary."""
        return {
            "consumed_kwh": self.metrics.total_energy_consumed_kwh,
            "recovered_kwh": self.metrics.total_energy_recovered_kwh,
            "net_kwh": self.metrics.net_energy_kwh,
            "efficiency": self.metrics.energy_efficiency,
            "solar_contribution_percent": 70.0 if self.solar_available else 0.0,
        }

    def export_metrics(self) -> str:
        """Export metrics as JSON."""
        data = {
            "system": "ARTEMIS-R",
            "version": "1.0",
            "export_time": datetime.now().isoformat(),
            "status": self.get_status(),
            "products": self.get_product_summary(),
            "energy": self.get_energy_summary(),
            "history": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "module": event.module,
                    "input_kg": event.input_mass_kg,
                    "output_kg": event.output_mass_kg,
                    "energy_kwh": event.energy_kwh,
                    "duration_hours": event.duration_hours,
                }
                for event in self.processing_history
            ],
        }
        return json.dumps(data, indent=2)


def run_artemis_simulation(
    crew_size: int = 4,
    days: int = 30,
    solar_available: bool = True,
) -> ARTEMISSystem:
    """
    Run a complete ARTEMIS-R simulation.

    Args:
        crew_size: Number of crew members
        days: Mission duration in days
        solar_available: Whether solar thermal is available

    Returns:
        Configured and run ARTEMISSystem
    """
    system = ARTEMISSystem(solar_available=solar_available)
    system.start()

    # Generate daily waste and process
    for day in range(days):
        # Get daily waste from all streams
        all_items = WasteStream.get_all_items()
        items = []
        masses = []

        for item in all_items:
            daily_mass = item.daily_mass_4_crew * (crew_size / 4.0)
            if daily_mass > 0:
                items.append(item)
                masses.append(daily_mass)

        # Add to hopper
        system.add_waste(items, masses)

        # Process all available waste
        system.process_all()

    return system


def print_artemis_summary(system: ARTEMISSystem) -> None:
    """Print a summary of ARTEMIS system performance."""
    print("\n" + "=" * 70)
    print("ARTEMIS-R SYSTEM PERFORMANCE SUMMARY")
    print("=" * 70)

    status = system.get_status()
    products = system.get_product_summary()
    energy = system.get_energy_summary()

    print(f"\nProcessing Runs: {status['metrics']['processing_runs']}")
    print(f"Total Input:     {status['metrics']['total_input_kg']:.2f} kg")
    print(f"Total Products:  {status['metrics']['total_products_kg']:.2f} kg")
    print(f"Mass Recovery:   {status['metrics']['mass_recovery_rate']:.1%}")

    print("\nPRODUCT BREAKDOWN:")
    print(f"  Syngas:           {products['syngas_kg']:.2f} kg")
    print(f"  Pyrolysis Oil:    {products['pyrolysis_oil_kg']:.2f} kg")
    print(f"  Biochar:          {products['biochar_kg']:.2f} kg")
    print(f"  3D Filament:      {products['filament_kg']:.2f} kg")
    print(f"  Composite Tiles:  {products['composite_tiles_kg']:.2f} kg")
    print(f"  Recovered Water:  {products['water_kg']:.2f} kg")
    print(f"  Recovered Metal:  {products['metal_kg']:.2f} kg")

    print("\nENERGY BALANCE:")
    print(f"  Consumed:         {energy['consumed_kwh']:.2f} kWh")
    print(f"  Recovered:        {energy['recovered_kwh']:.2f} kWh")
    print(f"  Net Energy:       {energy['net_kwh']:.2f} kWh")
    print(f"  Solar Contrib:    {energy['solar_contribution_percent']:.0f}%")

    net_status = "ENERGY POSITIVE" if energy["net_kwh"] > 0 else "ENERGY NEGATIVE"
    print(f"\n  Status: {net_status}")

    print("\n" + "=" * 70)
