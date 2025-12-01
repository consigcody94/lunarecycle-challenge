"""
Recycling system configuration and management.

Combines multiple recycling processes into an integrated system.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from lunarecycle.waste.streams import WasteItem, WasteCategory
from lunarecycle.recycling.processes import (
    RecyclingProcess,
    ProcessingResult,
    PyrolysisProcess,
    MeltExtrusionProcess,
    PlasmaProcess,
    HeatMeltCompaction,
    CompositeManufacturing,
    Product,
    ProductType,
)


class RecyclingTechnology(Enum):
    """Available recycling technologies."""
    PYROLYSIS = auto()
    MELT_EXTRUSION = auto()
    PLASMA_ARC = auto()
    HEAT_MELT_COMPACTION = auto()
    COMPOSITE_MANUFACTURING = auto()
    HYBRID = auto()  # Combination of multiple technologies


@dataclass
class SystemMetrics:
    """Performance metrics for a recycling system."""
    total_input_kg: float = 0.0
    total_output_kg: float = 0.0
    total_residue_kg: float = 0.0
    total_energy_consumed_kwh: float = 0.0
    total_energy_recovered_kwh: float = 0.0
    total_water_recovered_kg: float = 0.0
    total_processing_time_hrs: float = 0.0

    # Per-product outputs
    products_by_type: dict[ProductType, float] = field(default_factory=dict)

    # Quality metrics
    avg_quality_score: float = 0.0
    toxins_released: bool = False
    microplastics_generated: bool = False

    @property
    def mass_efficiency(self) -> float:
        """Overall mass recovery efficiency."""
        if self.total_input_kg > 0:
            return self.total_output_kg / self.total_input_kg
        return 0.0

    @property
    def net_energy_kwh(self) -> float:
        """Net energy (recovered - consumed)."""
        return self.total_energy_recovered_kwh - self.total_energy_consumed_kwh

    @property
    def energy_efficiency(self) -> float:
        """Energy recovery efficiency."""
        if self.total_energy_consumed_kwh > 0:
            return self.total_energy_recovered_kwh / self.total_energy_consumed_kwh
        return 0.0


@dataclass
class RecyclingSystem:
    """
    Integrated recycling system combining multiple processes.

    Can route different waste types to appropriate processes
    for optimal recycling efficiency.
    """
    name: str = "LunaRecycle System"
    technology: RecyclingTechnology = RecyclingTechnology.HYBRID
    processes: list[RecyclingProcess] = field(default_factory=list)

    # System constraints
    max_power_kw: float = 10.0  # Maximum power draw
    max_daily_capacity_kg: float = 20.0  # kg per day

    # Operating parameters
    operating_hours_per_day: float = 8.0
    crew_time_per_kg_hrs: float = 0.1  # Crew time required

    # Results tracking
    metrics: SystemMetrics = field(default_factory=SystemMetrics)
    processing_history: list[ProcessingResult] = field(default_factory=list)

    def __post_init__(self):
        if not self.processes:
            self._setup_default_processes()

    def _setup_default_processes(self):
        """Set up default processes based on technology type."""
        if self.technology == RecyclingTechnology.PYROLYSIS:
            self.processes = [PyrolysisProcess()]
        elif self.technology == RecyclingTechnology.MELT_EXTRUSION:
            self.processes = [MeltExtrusionProcess()]
        elif self.technology == RecyclingTechnology.PLASMA_ARC:
            self.processes = [PlasmaProcess()]
        elif self.technology == RecyclingTechnology.HEAT_MELT_COMPACTION:
            self.processes = [HeatMeltCompaction()]
        elif self.technology == RecyclingTechnology.COMPOSITE_MANUFACTURING:
            self.processes = [CompositeManufacturing()]
        elif self.technology == RecyclingTechnology.HYBRID:
            # Default hybrid system with multiple technologies
            self.processes = [
                MeltExtrusionProcess(output_form="filament"),
                CompositeManufacturing(),
                PyrolysisProcess(),
                HeatMeltCompaction(),
            ]

    def get_best_process(self, waste_item: WasteItem) -> Optional[RecyclingProcess]:
        """
        Find the best process for a given waste item.

        Priority:
        1. Mechanical recycling (filament/pellets) - highest value
        2. Composite manufacturing - for foams
        3. Pyrolysis - for organics
        4. Heat melt compaction - for everything else
        """
        # Try mechanical recycling first (highest value products)
        for proc in self.processes:
            if isinstance(proc, MeltExtrusionProcess) and proc.can_process(waste_item):
                return proc

        # Try composite manufacturing for foams
        if waste_item.category == WasteCategory.FOAM_PACKING:
            for proc in self.processes:
                if isinstance(proc, CompositeManufacturing) and proc.can_process(waste_item):
                    return proc

        # Try pyrolysis for organics
        for proc in self.processes:
            if isinstance(proc, PyrolysisProcess) and proc.can_process(waste_item):
                return proc

        # Fallback to heat melt compaction
        for proc in self.processes:
            if isinstance(proc, HeatMeltCompaction):
                return proc

        # Last resort - any process that can handle it
        for proc in self.processes:
            if proc.can_process(waste_item):
                return proc

        return None

    def process_waste(
        self,
        waste_items: list[WasteItem],
        masses_kg: list[float]
    ) -> ProcessingResult:
        """
        Process a batch of waste through the recycling system.

        Routes different waste types to appropriate processes.
        """
        # Group waste by best process
        process_batches: dict[RecyclingProcess, tuple[list[WasteItem], list[float]]] = {}

        for item, mass in zip(waste_items, masses_kg):
            best_process = self.get_best_process(item)
            if best_process:
                if best_process not in process_batches:
                    process_batches[best_process] = ([], [])
                process_batches[best_process][0].append(item)
                process_batches[best_process][1].append(mass)

        # Process each batch and combine results
        all_products: list[Product] = []
        total_input = sum(masses_kg)
        total_residue = 0.0
        total_energy_consumed = 0.0
        total_energy_recovered = 0.0
        total_time = 0.0
        toxins = False
        microplastics = False

        for process, (items, item_masses) in process_batches.items():
            result = process.process(items, item_masses)
            all_products.extend(result.products)
            total_residue += result.waste_residue_kg
            total_energy_consumed += result.energy_consumed_kwh
            total_energy_recovered += result.energy_recovered_kwh
            total_time += result.processing_time_hours
            toxins = toxins or result.toxins_released
            microplastics = microplastics or result.microplastics_generated

        # Create combined result
        combined_result = ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=all_products,
            waste_residue_kg=total_residue,
            mass_recovery_rate=sum(p.mass_kg for p in all_products) / total_input if total_input > 0 else 0,
            energy_consumed_kwh=total_energy_consumed,
            energy_recovered_kwh=total_energy_recovered,
            processing_time_hours=total_time,
            toxins_released=toxins,
            microplastics_generated=microplastics
        )

        # Update system metrics
        self._update_metrics(combined_result)
        self.processing_history.append(combined_result)

        return combined_result

    def _update_metrics(self, result: ProcessingResult):
        """Update cumulative system metrics."""
        self.metrics.total_input_kg += result.input_mass_kg
        self.metrics.total_output_kg += result.total_product_mass
        self.metrics.total_residue_kg += result.waste_residue_kg
        self.metrics.total_energy_consumed_kwh += result.energy_consumed_kwh
        self.metrics.total_energy_recovered_kwh += result.energy_recovered_kwh
        self.metrics.total_processing_time_hrs += result.processing_time_hours

        # Track products by type
        for product in result.products:
            if product.product_type not in self.metrics.products_by_type:
                self.metrics.products_by_type[product.product_type] = 0.0
            self.metrics.products_by_type[product.product_type] += product.mass_kg

            # Track water separately
            if product.product_type == ProductType.WATER:
                self.metrics.total_water_recovered_kg += product.mass_kg

        # Update quality metrics
        if result.products:
            total_quality = sum(p.quality_score * p.mass_kg for p in result.products)
            total_mass = sum(p.mass_kg for p in result.products)
            if total_mass > 0:
                new_avg = total_quality / total_mass
                # Running average
                if self.metrics.avg_quality_score > 0:
                    self.metrics.avg_quality_score = (
                        self.metrics.avg_quality_score * 0.9 + new_avg * 0.1
                    )
                else:
                    self.metrics.avg_quality_score = new_avg

        self.metrics.toxins_released = self.metrics.toxins_released or result.toxins_released
        self.metrics.microplastics_generated = (
            self.metrics.microplastics_generated or result.microplastics_generated
        )

    def reset_metrics(self):
        """Reset all accumulated metrics."""
        self.metrics = SystemMetrics()
        self.processing_history = []

    def get_summary(self) -> dict:
        """Get a summary of system performance."""
        return {
            "name": self.name,
            "technology": self.technology.name,
            "total_input_kg": self.metrics.total_input_kg,
            "total_output_kg": self.metrics.total_output_kg,
            "mass_efficiency": f"{self.metrics.mass_efficiency * 100:.1f}%",
            "total_residue_kg": self.metrics.total_residue_kg,
            "net_energy_kwh": self.metrics.net_energy_kwh,
            "energy_efficiency": f"{self.metrics.energy_efficiency * 100:.1f}%",
            "water_recovered_kg": self.metrics.total_water_recovered_kg,
            "processing_time_hrs": self.metrics.total_processing_time_hrs,
            "products": {
                pt.name: mass for pt, mass in self.metrics.products_by_type.items()
            },
            "quality_score": f"{self.metrics.avg_quality_score:.2f}",
            "safety": {
                "toxins_released": self.metrics.toxins_released,
                "microplastics": self.metrics.microplastics_generated
            }
        }

    def print_summary(self):
        """Print a formatted summary."""
        summary = self.get_summary()
        print("\n" + "=" * 60)
        print(f"RECYCLING SYSTEM: {summary['name']}")
        print(f"Technology: {summary['technology']}")
        print("=" * 60)

        print(f"\nMASS BALANCE:")
        print(f"  Input:      {summary['total_input_kg']:.2f} kg")
        print(f"  Output:     {summary['total_output_kg']:.2f} kg")
        print(f"  Residue:    {summary['total_residue_kg']:.2f} kg")
        print(f"  Efficiency: {summary['mass_efficiency']}")

        print(f"\nENERGY:")
        print(f"  Net Energy: {summary['net_energy_kwh']:.2f} kWh")
        print(f"  Efficiency: {summary['energy_efficiency']}")

        print(f"\nPRODUCTS:")
        for product, mass in summary['products'].items():
            print(f"  {product}: {mass:.2f} kg")

        print(f"\nWater Recovered: {summary['water_recovered_kg']:.2f} kg")
        print(f"Processing Time: {summary['processing_time_hrs']:.1f} hours")
        print(f"Quality Score: {summary['quality_score']}")

        print(f"\nSAFETY:")
        print(f"  Toxins Released: {'YES - WARNING' if summary['safety']['toxins_released'] else 'No'}")
        print(f"  Microplastics: {'YES - WARNING' if summary['safety']['microplastics'] else 'No'}")
        print("=" * 60)


def create_system(technology: str, **kwargs) -> RecyclingSystem:
    """Factory function to create recycling systems."""
    tech_map = {
        "pyrolysis": RecyclingTechnology.PYROLYSIS,
        "extrusion": RecyclingTechnology.MELT_EXTRUSION,
        "melt_extrusion": RecyclingTechnology.MELT_EXTRUSION,
        "plasma": RecyclingTechnology.PLASMA_ARC,
        "plasma_arc": RecyclingTechnology.PLASMA_ARC,
        "hmc": RecyclingTechnology.HEAT_MELT_COMPACTION,
        "heat_melt": RecyclingTechnology.HEAT_MELT_COMPACTION,
        "compaction": RecyclingTechnology.HEAT_MELT_COMPACTION,
        "composite": RecyclingTechnology.COMPOSITE_MANUFACTURING,
        "hybrid": RecyclingTechnology.HYBRID,
    }

    tech = tech_map.get(technology.lower(), RecyclingTechnology.HYBRID)
    return RecyclingSystem(technology=tech, **kwargs)
