"""
Core simulation engine for lunar waste recycling.

Integrates waste generation, accumulation, and recycling processes
over mission timelines.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import json

from lunarecycle.waste.streams import WasteStream, WasteItem, WasteCategory
from lunarecycle.waste.inventory import WasteInventory
from lunarecycle.recycling.systems import RecyclingSystem, create_system
from lunarecycle.recycling.processes import ProcessingResult
from lunarecycle.environment.lunar import (
    EnvironmentParameters,
    get_environment,
)


@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""

    # Mission parameters
    crew_size: int = 4
    mission_duration_days: int = 365
    location: str = "lunar_habitat"

    # Waste stream selection (None = all streams)
    waste_categories: Optional[list[WasteCategory]] = None
    waste_items: Optional[list[WasteItem]] = None

    # Processing parameters
    processing_frequency_days: int = 7  # How often to run recycling
    processing_batch_size_kg: float = 10.0  # Max batch size

    # System configuration
    recycling_technology: str = "hybrid"

    # Simulation settings
    start_date: datetime = field(default_factory=datetime.now)
    random_seed: Optional[int] = None

    def __post_init__(self):
        # Set default waste items if not specified
        if self.waste_items is None and self.waste_categories is None:
            self.waste_items = WasteStream.get_all_items()
        elif self.waste_items is None and self.waste_categories is not None:
            self.waste_items = []
            for cat in self.waste_categories:
                self.waste_items.extend(WasteStream.get_by_category(cat))


@dataclass
class DailyMetrics:
    """Metrics for a single simulation day."""

    day: int
    date: datetime
    waste_generated_kg: float
    waste_processed_kg: float
    waste_accumulated_kg: float
    products_produced_kg: float
    energy_consumed_kwh: float
    energy_recovered_kwh: float


@dataclass
class SimulationResults:
    """Complete results from a simulation run."""

    config: SimulationConfig
    environment: EnvironmentParameters

    # Summary metrics
    total_waste_generated_kg: float = 0.0
    total_waste_processed_kg: float = 0.0
    total_products_kg: float = 0.0
    total_residue_kg: float = 0.0

    # Efficiency metrics
    mass_recovery_rate: float = 0.0  # Products / Generated
    recycling_rate: float = 0.0  # Processed / Generated

    # Energy metrics
    total_energy_consumed_kwh: float = 0.0
    total_energy_recovered_kwh: float = 0.0
    net_energy_kwh: float = 0.0

    # Product breakdown
    products_by_type: dict[str, float] = field(default_factory=dict)

    # Time series data
    daily_metrics: list[DailyMetrics] = field(default_factory=list)

    # Processing results
    processing_events: list[ProcessingResult] = field(default_factory=list)

    # Challenge scoring (based on NASA criteria)
    score_breakdown: dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0

    def to_dict(self) -> dict:
        """Convert results to dictionary."""
        return {
            "summary": {
                "mission_duration_days": self.config.mission_duration_days,
                "crew_size": self.config.crew_size,
                "location": self.config.location,
                "total_waste_generated_kg": round(self.total_waste_generated_kg, 2),
                "total_waste_processed_kg": round(self.total_waste_processed_kg, 2),
                "total_products_kg": round(self.total_products_kg, 2),
                "total_residue_kg": round(self.total_residue_kg, 2),
                "mass_recovery_rate": f"{self.mass_recovery_rate * 100:.1f}%",
                "recycling_rate": f"{self.recycling_rate * 100:.1f}%",
            },
            "energy": {
                "consumed_kwh": round(self.total_energy_consumed_kwh, 2),
                "recovered_kwh": round(self.total_energy_recovered_kwh, 2),
                "net_kwh": round(self.net_energy_kwh, 2),
            },
            "products": self.products_by_type,
            "scoring": {
                "breakdown": self.score_breakdown,
                "total": round(self.total_score, 2),
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert results to JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    def print_summary(self):
        """Print formatted summary."""
        print("\n" + "=" * 70)
        print("SIMULATION RESULTS")
        print("=" * 70)

        print("\nMISSION PARAMETERS:")
        print(f"  Duration: {self.config.mission_duration_days} days")
        print(f"  Crew Size: {self.config.crew_size}")
        print(f"  Location: {self.config.location}")
        print(f"  Technology: {self.config.recycling_technology}")

        print("\nMASS BALANCE:")
        print(f"  Waste Generated:  {self.total_waste_generated_kg:,.1f} kg")
        print(f"  Waste Processed:  {self.total_waste_processed_kg:,.1f} kg")
        print(f"  Products Created: {self.total_products_kg:,.1f} kg")
        print(f"  Residue:          {self.total_residue_kg:,.1f} kg")
        print(f"  Recycling Rate:   {self.recycling_rate * 100:.1f}%")
        print(f"  Recovery Rate:    {self.mass_recovery_rate * 100:.1f}%")

        print("\nENERGY BALANCE:")
        print(f"  Energy Consumed:  {self.total_energy_consumed_kwh:,.1f} kWh")
        print(f"  Energy Recovered: {self.total_energy_recovered_kwh:,.1f} kWh")
        print(f"  Net Energy:       {self.net_energy_kwh:,.1f} kWh")

        print("\nPRODUCTS PRODUCED:")
        for product, mass in sorted(self.products_by_type.items(), key=lambda x: -x[1]):
            print(f"  {product}: {mass:,.1f} kg")

        if self.score_breakdown:
            print("\nCHALLENGE SCORING:")
            for criterion, score in self.score_breakdown.items():
                print(f"  {criterion}: {score:.1f}")
            print(f"  TOTAL SCORE: {self.total_score:.1f}")

        print("=" * 70)


class Simulation:
    """
    Main simulation engine for lunar waste recycling.

    Simulates waste generation, accumulation, and processing
    over a mission timeline.
    """

    def __init__(
        self,
        crew_size: int = 4,
        mission_duration_days: int = 365,
        location: str = "lunar_habitat",
        **kwargs,
    ):
        """
        Initialize simulation.

        Args:
            crew_size: Number of crew members
            mission_duration_days: Mission length in days
            location: Operating location
            **kwargs: Additional config options
        """
        self.config = SimulationConfig(
            crew_size=crew_size,
            mission_duration_days=mission_duration_days,
            location=location,
            **kwargs,
        )

        # Initialize components
        self.environment = get_environment(location)
        self.inventory = WasteInventory(crew_size=crew_size, mission_start=self.config.start_date)
        self.recycling_system: Optional[RecyclingSystem] = None

        # Track selected waste streams
        self._waste_items: list[WasteItem] = self.config.waste_items or []

    def add_waste_stream(self, waste_item: WasteItem):
        """Add a waste stream to the simulation."""
        if waste_item not in self._waste_items:
            self._waste_items.append(waste_item)

    def add_waste_category(self, category: WasteCategory):
        """Add all items from a waste category."""
        for item in WasteStream.get_by_category(category):
            self.add_waste_stream(item)

    def set_recycling_system(self, system: RecyclingSystem):
        """Set the recycling system to use."""
        self.recycling_system = system

    def add_recycling_system(self, system: RecyclingSystem):
        """Alias for set_recycling_system."""
        self.set_recycling_system(system)

    def _create_default_system(self) -> RecyclingSystem:
        """Create default recycling system based on config."""
        return create_system(
            self.config.recycling_technology,
            name=f"LunaRecycle-{self.config.recycling_technology.title()}",
        )

    def run(self) -> SimulationResults:
        """
        Run the simulation.

        Returns:
            SimulationResults with all metrics and data
        """
        # Ensure we have a recycling system
        if self.recycling_system is None:
            self.recycling_system = self._create_default_system()

        # Initialize results
        results = SimulationResults(config=self.config, environment=self.environment)

        # Simulation loop
        for day in range(self.config.mission_duration_days):
            current_date = self.config.start_date + timedelta(days=day)

            # Generate daily waste
            daily_waste = self._calculate_daily_waste()
            self.inventory.add_daily_waste(current_date, self._waste_items)

            # Process waste on scheduled days
            processed_today = 0.0
            products_today = 0.0
            energy_consumed = 0.0
            energy_recovered = 0.0

            if day > 0 and day % self.config.processing_frequency_days == 0:
                # Get accumulated waste to process
                batch_items = []
                batch_masses = []

                for item in self._waste_items:
                    available = self.inventory.get_unprocessed_by_item(item.name)
                    if available > 0:
                        # Limit to batch size
                        to_process = min(available, self.config.processing_batch_size_kg)
                        batch_items.append(item)
                        batch_masses.append(to_process)

                        # Mark as processed in inventory
                        self.inventory.process_waste(item, to_process, current_date)

                if batch_items:
                    # Run recycling process
                    result = self.recycling_system.process_waste(batch_items, batch_masses)
                    results.processing_events.append(result)

                    processed_today = result.input_mass_kg
                    products_today = result.total_product_mass
                    energy_consumed = result.energy_consumed_kwh
                    energy_recovered = result.energy_recovered_kwh

                    # Update product totals
                    for product in result.products:
                        ptype = product.product_type.name
                        if ptype not in results.products_by_type:
                            results.products_by_type[ptype] = 0.0
                        results.products_by_type[ptype] += product.mass_kg

            # Record daily metrics
            daily = DailyMetrics(
                day=day,
                date=current_date,
                waste_generated_kg=daily_waste,
                waste_processed_kg=processed_today,
                waste_accumulated_kg=self.inventory.total_remaining_kg,
                products_produced_kg=products_today,
                energy_consumed_kwh=energy_consumed,
                energy_recovered_kwh=energy_recovered,
            )
            results.daily_metrics.append(daily)

        # Calculate final metrics
        results.total_waste_generated_kg = self.inventory.total_generated_kg
        results.total_waste_processed_kg = self.inventory.total_processed_kg
        results.total_products_kg = self.recycling_system.metrics.total_output_kg
        results.total_residue_kg = self.recycling_system.metrics.total_residue_kg

        if results.total_waste_generated_kg > 0:
            results.recycling_rate = (
                results.total_waste_processed_kg / results.total_waste_generated_kg
            )
            results.mass_recovery_rate = (
                results.total_products_kg / results.total_waste_generated_kg
            )

        results.total_energy_consumed_kwh = self.recycling_system.metrics.total_energy_consumed_kwh
        results.total_energy_recovered_kwh = (
            self.recycling_system.metrics.total_energy_recovered_kwh
        )
        results.net_energy_kwh = (
            results.total_energy_recovered_kwh - results.total_energy_consumed_kwh
        )

        # Calculate challenge score
        self._calculate_score(results)

        return results

    def _calculate_daily_waste(self) -> float:
        """Calculate total daily waste generation."""
        return sum(
            item.mass_per_unit_kg * item.generation_rate_per_crew_day * self.config.crew_size
            for item in self._waste_items
        )

    def _calculate_score(self, results: SimulationResults):
        """
        Calculate challenge score based on NASA LunaRecycle criteria.

        Scoring based on:
        - Recycling efficiency (% of waste processed)
        - Mass recovery (products / waste)
        - Energy efficiency
        - Safety (no toxins, no microplastics)
        - Difficulty bonus (processing harder materials)
        """
        scores = {}

        # Recycling efficiency (max 30 points)
        recycling_score = min(30, results.recycling_rate * 30)
        scores["Recycling Efficiency"] = recycling_score

        # Mass recovery (max 25 points)
        recovery_score = min(25, results.mass_recovery_rate * 25)
        scores["Mass Recovery"] = recovery_score

        # Energy efficiency (max 15 points)
        if results.total_energy_consumed_kwh > 0:
            energy_ratio = results.total_energy_recovered_kwh / results.total_energy_consumed_kwh
            energy_score = min(15, energy_ratio * 15)
        else:
            energy_score = 0
        scores["Energy Efficiency"] = energy_score

        # Safety (max 15 points)
        safety_score = 15
        if self.recycling_system.metrics.toxins_released:
            safety_score -= 10
        if self.recycling_system.metrics.microplastics_generated:
            safety_score -= 5
        scores["Safety"] = max(0, safety_score)

        # Difficulty bonus (max 15 points)
        # Bonus for processing difficult materials (Level 2 and 3)
        difficulty_items = sum(1 for item in self._waste_items if item.difficulty.value >= 2)
        difficulty_score = min(15, difficulty_items * 3)
        scores["Difficulty Bonus"] = difficulty_score

        results.score_breakdown = scores
        results.total_score = sum(scores.values())


# Convenience functions
def quick_simulation(
    days: int = 365, technology: str = "hybrid", location: str = "lunar_habitat"
) -> SimulationResults:
    """
    Run a quick simulation with default parameters.

    Args:
        days: Mission duration
        technology: Recycling technology to use
        location: Operating location

    Returns:
        SimulationResults
    """
    sim = Simulation(
        crew_size=4, mission_duration_days=days, location=location, recycling_technology=technology
    )
    return sim.run()


if __name__ == "__main__":
    # Demo simulation
    print("Running LunaRecycle simulation...")
    results = quick_simulation(days=365)
    results.print_summary()
