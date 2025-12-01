"""
Tests for the LunaRecycle simulation system.

Run with: pytest tests/
"""

import pytest
from datetime import datetime

from lunarecycle.waste.streams import (
    WasteStream,
    WasteCategory,
    DifficultyLevel,
)
from lunarecycle.waste.inventory import WasteInventory
from lunarecycle.waste.materials import Material, MaterialType
from lunarecycle.recycling.systems import RecyclingSystem, RecyclingTechnology, create_system
from lunarecycle.recycling.processes import (
    PyrolysisProcess,
    MeltExtrusionProcess,
    HeatMeltCompaction,
)
from lunarecycle.environment.lunar import LunarEnvironment, get_environment
from lunarecycle.simulation.engine import Simulation


class TestWasteStreams:
    """Tests for waste stream definitions."""

    def test_all_items_defined(self):
        """Test that all waste items are properly defined."""
        items = WasteStream.get_all_items()
        assert len(items) >= 14  # Minimum expected items

    def test_categories_have_items(self):
        """Test that all categories have at least one item."""
        for category in WasteCategory:
            items = WasteStream.get_by_category(category)
            assert len(items) > 0, f"Category {category.name} has no items"

    def test_daily_mass_calculation(self):
        """Test daily mass calculation for 4-crew."""
        item = WasteStream.FOOD_PACKAGING_FILM
        daily = item.daily_mass_4_crew
        # Should be mass * rate * 4
        expected = item.mass_per_unit_kg * item.generation_rate_per_crew_day * 4
        assert daily == pytest.approx(expected)

    def test_annual_mass_calculation(self):
        """Test annual mass calculation."""
        item = WasteStream.FOOD_PACKAGING_FILM
        annual = item.annual_mass_4_crew
        assert annual == pytest.approx(item.daily_mass_4_crew * 365)

    def test_total_daily_mass_reasonable(self):
        """Test that total daily mass is in expected range."""
        total = WasteStream.get_total_daily_mass_4_crew()
        # NASA estimates ~2 kg/astronaut/day total, but our model focuses on
        # recyclable non-metabolic waste which is ~1.2-1.5 kg/astronaut/day
        # Total for 4-crew: 4.8-6.0 kg/day
        assert 4.0 <= total <= 8.0  # 4-crew recyclable waste range

    def test_difficulty_levels_assigned(self):
        """Test that difficulty levels are properly assigned."""
        zotek = WasteStream.ZOTEK_FOAM
        assert zotek.difficulty == DifficultyLevel.LEVEL_3  # Hardest

        film = WasteStream.FOOD_PACKAGING_FILM
        assert film.difficulty == DifficultyLevel.LEVEL_1  # Easiest


class TestMaterials:
    """Tests for material property database."""

    def test_materials_defined(self):
        """Test that key materials are defined."""
        assert Material.LDPE is not None
        assert Material.HDPE is not None
        assert Material.PP is not None
        assert Material.PVDF is not None
        assert Material.COTTON is not None

    def test_material_lookup(self):
        """Test material lookup by name."""
        ldpe = Material.get_by_name("LDPE")
        assert ldpe is not None
        assert "Polyethylene" in ldpe.name

    def test_thermoplastics_filter(self):
        """Test filtering thermoplastics."""
        plastics = Material.get_thermoplastics()
        assert len(plastics) >= 3
        for mat in plastics:
            assert mat.material_type == MaterialType.THERMOPLASTIC

    def test_pyrolysis_yields_sum(self):
        """Test that pyrolysis yields don't exceed 100%."""
        for mat in Material.get_all():
            total = (
                mat.pyrolysis.syngas_yield_percent
                + mat.pyrolysis.oil_yield_percent
                + mat.pyrolysis.char_yield_percent
                + mat.pyrolysis.water_yield_percent
            )
            assert total <= 101.0, f"{mat.name} pyrolysis yields sum to {total}%"


class TestWasteInventory:
    """Tests for waste inventory tracking."""

    def test_inventory_creation(self):
        """Test creating an inventory."""
        inv = WasteInventory(crew_size=4)
        assert inv.crew_size == 4
        assert inv.total_generated_kg == 0.0

    def test_daily_waste_accumulation(self):
        """Test adding daily waste."""
        inv = WasteInventory(crew_size=4)
        inv.add_daily_waste(datetime.now())
        assert inv.total_generated_kg > 0
        assert inv.total_remaining_kg > 0

    def test_multi_day_simulation(self):
        """Test simulating multiple days."""
        inv = WasteInventory(crew_size=4)
        inv.simulate_accumulation(days=30)
        assert len(inv.entries) > 0
        assert inv.total_generated_kg > 0

    def test_waste_processing(self):
        """Test processing waste."""
        inv = WasteInventory(crew_size=4)
        inv.simulate_accumulation(days=7)

        initial = inv.total_remaining_kg
        item = WasteStream.FOOD_PACKAGING_FILM
        processed = inv.process_waste(item, 1.0, datetime.now())

        assert processed > 0
        assert inv.total_processed_kg > 0
        assert inv.total_remaining_kg < initial


class TestRecyclingProcesses:
    """Tests for recycling process models."""

    def test_pyrolysis_can_process(self):
        """Test pyrolysis process compatibility."""
        proc = PyrolysisProcess()

        # Should process plastics
        assert proc.can_process(WasteStream.FOOD_PACKAGING_FILM)
        assert proc.can_process(WasteStream.COTTON_CLOTHING)

    def test_pyrolysis_processing(self):
        """Test pyrolysis produces outputs."""
        proc = PyrolysisProcess()
        items = [WasteStream.FOOD_PACKAGING_FILM]
        masses = [1.0]

        result = proc.process(items, masses)

        assert result.input_mass_kg == 1.0
        assert len(result.products) > 0
        assert result.total_product_mass > 0

    def test_melt_extrusion_filters(self):
        """Test melt extrusion only processes thermoplastics."""
        proc = MeltExtrusionProcess()

        assert proc.can_process(WasteStream.FOOD_PACKAGING_FILM)
        assert not proc.can_process(WasteStream.COTTON_CLOTHING)
        assert not proc.can_process(WasteStream.PAPER)

    def test_hmc_processes_all(self):
        """Test heat melt compaction can process anything."""
        proc = HeatMeltCompaction()

        for item in WasteStream.get_all_items():
            assert proc.can_process(item), f"HMC should process {item.name}"

    def test_energy_requirement(self):
        """Test energy calculations."""
        proc = PyrolysisProcess()
        energy = proc.get_energy_requirement(10.0)
        assert energy > 0


class TestRecyclingSystem:
    """Tests for integrated recycling systems."""

    def test_system_creation(self):
        """Test creating a recycling system."""
        system = RecyclingSystem(technology=RecyclingTechnology.HYBRID)
        assert system.name is not None
        assert len(system.processes) > 0

    def test_system_factory(self):
        """Test system factory function."""
        for tech in ["pyrolysis", "plasma", "hybrid"]:
            system = create_system(tech)
            assert system is not None

    def test_system_processing(self):
        """Test system processes waste."""
        system = create_system("hybrid")
        items = [WasteStream.FOOD_PACKAGING_FILM, WasteStream.COTTON_CLOTHING]
        masses = [1.0, 0.5]

        result = system.process_waste(items, masses)

        assert result.input_mass_kg == 1.5
        assert len(result.products) > 0

    def test_system_metrics_update(self):
        """Test system metrics are updated."""
        system = create_system("hybrid")
        items = [WasteStream.FOOD_PACKAGING_FILM]
        masses = [1.0]

        system.process_waste(items, masses)

        assert system.metrics.total_input_kg > 0
        assert system.metrics.total_output_kg > 0


class TestEnvironment:
    """Tests for environment parameters."""

    def test_lunar_surface(self):
        """Test lunar surface environment."""
        env = LunarEnvironment.surface()
        assert env.gravity_m_s2 == pytest.approx(1.62)
        assert env.atmosphere.pressure_kpa == 0.0  # Vacuum

    def test_lunar_habitat(self):
        """Test lunar habitat environment."""
        env = LunarEnvironment.habitat()
        assert env.atmosphere.pressure_kpa == pytest.approx(101.3)
        assert env.thermal.avg_temp_c == pytest.approx(22.0)

    def test_environment_factory(self):
        """Test environment factory function."""
        for loc in ["lunar_habitat", "lunar_surface", "mars_habitat"]:
            env = get_environment(loc)
            assert env is not None

    def test_invalid_location(self):
        """Test invalid location raises error."""
        with pytest.raises(ValueError):
            get_environment("invalid_location")


class TestSimulation:
    """Tests for the simulation engine."""

    def test_simulation_creation(self):
        """Test creating a simulation."""
        sim = Simulation(crew_size=4, mission_duration_days=30, location="lunar_habitat")
        assert sim.config.crew_size == 4
        assert sim.config.mission_duration_days == 30

    def test_simulation_run(self):
        """Test running a simulation."""
        sim = Simulation(crew_size=4, mission_duration_days=30, location="lunar_habitat")
        results = sim.run()

        assert results.total_waste_generated_kg > 0
        assert results.total_waste_processed_kg > 0
        assert len(results.daily_metrics) == 30

    def test_simulation_scoring(self):
        """Test simulation calculates scores."""
        sim = Simulation(crew_size=4, mission_duration_days=30, location="lunar_habitat")
        results = sim.run()

        assert results.total_score > 0
        assert len(results.score_breakdown) > 0

    def test_simulation_results_export(self):
        """Test results can be exported."""
        sim = Simulation(crew_size=4, mission_duration_days=7)
        results = sim.run()

        # Test JSON export
        json_str = results.to_json()
        assert len(json_str) > 0
        assert "summary" in json_str

        # Test dict export
        d = results.to_dict()
        assert "summary" in d
        assert "energy" in d


class TestIntegration:
    """Integration tests for full system."""

    def test_full_year_simulation(self):
        """Test a full year simulation."""
        sim = Simulation(
            crew_size=4,
            mission_duration_days=365,
            location="lunar_habitat",
            recycling_technology="hybrid",
        )
        results = sim.run()

        # Our model estimates ~1800-2200 kg/year for 4 crew (recyclable waste only)
        # NASA's 2100-2600 kg includes some metabolic waste we don't model
        assert 1500 <= results.total_waste_generated_kg <= 2500

        # Should process most waste
        assert results.recycling_rate > 0.5

        # Should have positive recovery
        assert results.mass_recovery_rate > 0.3

    def test_different_technologies(self):
        """Test different technologies produce different results."""
        results = {}
        for tech in ["pyrolysis", "plasma", "hybrid"]:
            sim = Simulation(crew_size=4, mission_duration_days=30, recycling_technology=tech)
            results[tech] = sim.run()

        # Different technologies should have different energy profiles
        assert results["pyrolysis"].net_energy_kwh != results["plasma"].net_energy_kwh


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
