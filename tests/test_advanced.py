"""
Advanced tests for LunaRecycle simulation system.

Tests mass/energy conservation, edge cases, scoring algorithms,
and performance characteristics.
"""

import pytest

from lunarecycle.waste.streams import (
    WasteStream,
)
from lunarecycle.waste.inventory import WasteInventory
from lunarecycle.waste.materials import Material
from lunarecycle.recycling.systems import create_system
from lunarecycle.recycling.processes import (
    PyrolysisProcess,
    MeltExtrusionProcess,
    PlasmaProcess,
    HeatMeltCompaction,
    CompositeManufacturing,
    ProductType,
)
from lunarecycle.environment.lunar import LunarEnvironment, MarsEnvironment, get_environment
from lunarecycle.simulation.engine import Simulation


class TestMassConservation:
    """Tests for mass balance conservation."""

    def test_pyrolysis_mass_balance(self):
        """Test that pyrolysis has reasonable mass balance."""
        proc = PyrolysisProcess()
        items = [WasteStream.FOOD_PACKAGING_FILM, WasteStream.COTTON_CLOTHING]
        masses = [5.0, 3.0]
        total_input = sum(masses)

        result = proc.process(items, masses)

        # Total output (products + residue) should be close to input
        # Some variation allowed due to water/gas release and recovery
        total_output = result.total_product_mass + result.waste_residue_kg
        # Allow up to 15% variation (water absorbed from atmosphere, etc.)
        assert 0.85 <= (total_output / total_input) <= 1.15

    def test_melt_extrusion_mass_balance(self):
        """Test melt extrusion mass conservation."""
        proc = MeltExtrusionProcess()
        items = [WasteStream.FOOD_PACKAGING_FILM, WasteStream.BEVERAGE_CONTAINER]
        masses = [2.0, 1.5]
        total_input = sum(masses)

        result = proc.process(items, masses)

        # Account for rejected mass + products + residue
        total_output = result.total_product_mass + result.waste_residue_kg
        assert total_output <= total_input * 1.01

    def test_plasma_mass_balance(self):
        """Test plasma process mass conservation."""
        proc = PlasmaProcess()
        items = WasteStream.get_all_items()[:5]
        masses = [1.0] * 5

        result = proc.process(items, masses)

        # Plasma should have very high recovery
        assert result.mass_recovery_rate >= 0.95

    def test_simulation_mass_balance(self):
        """Test overall simulation mass balance."""
        sim = Simulation(crew_size=4, mission_duration_days=30, location="lunar_habitat")
        results = sim.run()

        # Generated = Processed + Unprocessed
        unprocessed = results.total_waste_generated_kg - results.total_waste_processed_kg
        assert unprocessed >= 0

        # Products + Residue <= Processed
        output_total = results.total_products_kg + results.total_residue_kg
        # Allow some tolerance for floating point
        assert output_total <= results.total_waste_processed_kg * 1.05


class TestEnergyBalance:
    """Tests for energy calculations."""

    def test_pyrolysis_energy_positive(self):
        """Test pyrolysis produces positive energy."""
        proc = PyrolysisProcess()
        items = [WasteStream.FOOD_PACKAGING_FILM]  # High energy plastic
        masses = [10.0]

        result = proc.process(items, masses)

        # Should consume energy for heating
        assert result.energy_consumed_kwh > 0
        # Should recover energy from products
        assert result.energy_recovered_kwh > 0

    def test_energy_requirement_scales_with_mass(self):
        """Test energy requirements scale linearly with mass."""
        proc = PyrolysisProcess()

        energy_1kg = proc.get_energy_requirement(1.0)
        energy_10kg = proc.get_energy_requirement(10.0)

        assert abs(energy_10kg - energy_1kg * 10) < 0.001

    def test_plasma_high_energy_consumption(self):
        """Test plasma process has highest energy consumption."""
        items = [WasteStream.FOOD_PACKAGING_FILM]
        masses = [5.0]

        pyro = PyrolysisProcess()
        plasma = PlasmaProcess()

        pyro_result = pyro.process(items, masses)
        plasma_result = plasma.process(items, masses)

        # Plasma should consume more energy
        assert plasma_result.energy_consumed_kwh > pyro_result.energy_consumed_kwh


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_mass_processing(self):
        """Test processing with zero mass."""
        proc = PyrolysisProcess()
        items = [WasteStream.FOOD_PACKAGING_FILM]
        masses = [0.0]

        result = proc.process(items, masses)

        assert result.input_mass_kg == 0.0
        assert result.total_product_mass == 0.0

    def test_empty_waste_list(self):
        """Test processing with empty waste list."""
        proc = PyrolysisProcess()

        result = proc.process([], [])

        assert result.input_mass_kg == 0.0
        assert len(result.products) == 0

    def test_single_day_simulation(self):
        """Test simulation with single day."""
        sim = Simulation(crew_size=4, mission_duration_days=1, location="lunar_habitat")
        results = sim.run()

        assert len(results.daily_metrics) == 1
        assert results.total_waste_generated_kg > 0

    def test_large_crew_simulation(self):
        """Test simulation with large crew."""
        sim = Simulation(crew_size=10, mission_duration_days=30, location="lunar_habitat")
        results = sim.run()

        # Waste should scale with crew size
        sim_4crew = Simulation(crew_size=4, mission_duration_days=30)
        results_4crew = sim_4crew.run()

        ratio = results.total_waste_generated_kg / results_4crew.total_waste_generated_kg
        assert 2.3 <= ratio <= 2.7  # Should be ~2.5x (10/4)

    def test_frequent_processing(self):
        """Test simulation with daily processing."""
        sim = Simulation(
            crew_size=4,
            mission_duration_days=30,
            location="lunar_habitat",
            processing_frequency_days=1,
        )
        results = sim.run()

        # Should have high recycling rate with frequent processing
        assert results.recycling_rate > 0.9

    def test_infrequent_processing(self):
        """Test simulation with infrequent processing."""
        sim = Simulation(
            crew_size=4,
            mission_duration_days=30,
            location="lunar_habitat",
            processing_frequency_days=30,
        )
        results = sim.run()

        # Should process in one big batch at end
        # Will have lower rate since only one processing event
        assert results.recycling_rate < 0.5  # Only processed once

    def test_incompatible_waste_for_process(self):
        """Test processing waste that's incompatible with process."""
        proc = MeltExtrusionProcess()

        # Cotton is not compatible with melt extrusion
        assert not proc.can_process(WasteStream.COTTON_CLOTHING)

        # Processing should reject incompatible items
        result = proc.process([WasteStream.COTTON_CLOTHING], [1.0])
        assert result.total_product_mass == 0.0


class TestScoringAlgorithm:
    """Tests for challenge scoring calculations."""

    def test_score_components(self):
        """Test that score components are calculated correctly."""
        sim = Simulation(crew_size=4, mission_duration_days=30, location="lunar_habitat")
        results = sim.run()

        # Check all score components exist
        assert "Recycling Efficiency" in results.score_breakdown
        assert "Mass Recovery" in results.score_breakdown
        assert "Energy Efficiency" in results.score_breakdown
        assert "Safety" in results.score_breakdown
        assert "Difficulty Bonus" in results.score_breakdown

    def test_score_max_values(self):
        """Test that scores don't exceed maximums."""
        sim = Simulation(crew_size=4, mission_duration_days=30, location="lunar_habitat")
        results = sim.run()

        # Check individual maximums
        assert results.score_breakdown["Recycling Efficiency"] <= 30
        assert results.score_breakdown["Mass Recovery"] <= 25
        assert results.score_breakdown["Energy Efficiency"] <= 15
        assert results.score_breakdown["Safety"] <= 15
        assert results.score_breakdown["Difficulty Bonus"] <= 15

        # Total should not exceed 100
        assert results.total_score <= 100

    def test_score_positivity(self):
        """Test that all scores are non-negative."""
        sim = Simulation(crew_size=4, mission_duration_days=30, location="lunar_habitat")
        results = sim.run()

        for name, score in results.score_breakdown.items():
            assert score >= 0, f"{name} score is negative: {score}"

        assert results.total_score >= 0

    def test_difficulty_bonus_calculation(self):
        """Test difficulty bonus for processing hard materials."""
        # Simulation with all items (includes Level 3 Zotek foam)
        sim_all = Simulation(crew_size=4, mission_duration_days=30, location="lunar_habitat")
        results_all = sim_all.run()

        # Simulation with only easy items
        sim_easy = Simulation(
            crew_size=4,
            mission_duration_days=30,
            location="lunar_habitat",
            waste_items=[WasteStream.FOOD_PACKAGING_FILM, WasteStream.TAPE],
        )
        results_easy = sim_easy.run()

        # All items should have higher difficulty bonus
        assert (
            results_all.score_breakdown["Difficulty Bonus"]
            > results_easy.score_breakdown["Difficulty Bonus"]
        )


class TestRecyclingTechnologies:
    """Tests for individual recycling technologies."""

    def test_all_technologies_instantiate(self):
        """Test all technology types can be created."""
        for tech in ["pyrolysis", "melt_extrusion", "plasma", "hybrid", "compaction"]:
            system = create_system(tech)
            assert system is not None
            assert len(system.processes) > 0

    def test_hybrid_system_routes_correctly(self):
        """Test hybrid system routes waste to best process."""
        system = create_system("hybrid")

        # Thermoplastic should go to melt extrusion (highest value)
        best = system.get_best_process(WasteStream.FOOD_PACKAGING_FILM)
        assert isinstance(best, MeltExtrusionProcess)

        # Foam should go to composite manufacturing
        best = system.get_best_process(WasteStream.ZOTEK_FOAM)
        assert isinstance(best, CompositeManufacturing)

        # Cotton should go to pyrolysis
        best = system.get_best_process(WasteStream.COTTON_CLOTHING)
        assert isinstance(best, PyrolysisProcess)

    def test_product_types_generated(self):
        """Test each technology produces expected product types."""
        # Pyrolysis should produce syngas, oil, char
        pyro = PyrolysisProcess()
        result = pyro.process([WasteStream.FOOD_PACKAGING_FILM], [5.0])
        product_types = {p.product_type for p in result.products}
        assert ProductType.SYNGAS in product_types
        assert ProductType.PYROLYSIS_OIL in product_types

        # Melt extrusion should produce filament
        melt = MeltExtrusionProcess()
        result = melt.process([WasteStream.FOOD_PACKAGING_FILM], [5.0])
        product_types = {p.product_type for p in result.products}
        assert ProductType.FILAMENT in product_types

        # HMC should produce composite tiles
        hmc = HeatMeltCompaction()
        result = hmc.process([WasteStream.FOOD_PACKAGING_FILM], [5.0])
        product_types = {p.product_type for p in result.products}
        assert ProductType.COMPOSITE in product_types


class TestEnvironments:
    """Tests for environment configurations."""

    def test_lunar_environments(self):
        """Test lunar environment configurations."""
        surface = LunarEnvironment.surface()
        habitat = LunarEnvironment.habitat()

        # Surface is vacuum, habitat is pressurized
        assert surface.atmosphere.pressure_kpa == 0.0
        assert habitat.atmosphere.pressure_kpa > 100.0

        # Both have lunar gravity
        assert surface.gravity_m_s2 == habitat.gravity_m_s2

    def test_mars_environments(self):
        """Test Mars environment configurations."""
        surface = MarsEnvironment.surface()
        habitat = MarsEnvironment.habitat()

        # Mars has thin atmosphere, not vacuum
        assert 0 < surface.atmosphere.pressure_kpa < 1.0
        assert habitat.atmosphere.pressure_kpa > 100.0

        # Mars gravity is higher than Moon
        assert surface.gravity_m_s2 > LunarEnvironment.LUNAR_GRAVITY

    def test_environment_factory(self):
        """Test environment factory handles various inputs."""
        valid_locations = [
            "lunar_habitat",
            "lunar_surface",
            "mars_habitat",
            "mars_surface",
            "moon_habitat",  # Alias
            "moon_surface",  # Alias
        ]

        for loc in valid_locations:
            env = get_environment(loc)
            assert env is not None

    def test_environment_power_constraints(self):
        """Test power constraints vary by location."""
        lunar = get_environment("lunar_habitat")
        mars = get_environment("mars_habitat")

        # Lunar should have more solar power available
        assert lunar.power.avg_power_kw >= mars.power.avg_power_kw


class TestPerformance:
    """Performance and stress tests."""

    def test_long_simulation(self):
        """Test simulation over 5 years."""
        sim = Simulation(
            crew_size=4,
            mission_duration_days=365 * 5,  # 5 years
            location="lunar_habitat",
            processing_frequency_days=7,
        )
        results = sim.run()

        assert len(results.daily_metrics) == 365 * 5
        assert results.total_waste_generated_kg > 5000  # Should be significant

    def test_many_processing_events(self):
        """Test simulation with many processing events."""
        sim = Simulation(
            crew_size=4,
            mission_duration_days=365,
            location="lunar_habitat",
            processing_frequency_days=1,  # Daily processing
        )
        results = sim.run()

        # Should have ~365 processing events
        assert len(results.processing_events) > 300

    def test_inventory_performance(self):
        """Test inventory handles large number of entries."""
        inv = WasteInventory(crew_size=4)
        inv.simulate_accumulation(days=365)

        # Should have many entries
        assert len(inv.entries) > 5000

        # Should still be able to get summaries quickly
        summary = inv.get_category_summary()
        assert len(summary) > 0


class TestMaterialProperties:
    """Tests for material property database."""

    def test_all_materials_have_required_properties(self):
        """Test all materials have complete properties."""
        for mat in Material.get_all():
            assert mat.density_kg_m3 > 0
            assert mat.heating_value_mj_kg >= 0
            assert mat.thermal is not None
            assert mat.chemical is not None
            assert mat.pyrolysis is not None

    def test_material_lookup_variations(self):
        """Test material lookup with different inputs."""
        # Short codes
        assert Material.get_by_name("LDPE") is not None
        assert Material.get_by_name("ldpe") is not None
        assert Material.get_by_name("PE") is not None

        # Full names
        assert Material.get_by_name("Low-Density Polyethylene") is not None
        assert Material.get_by_name("polyethylene") is not None

    def test_pfas_materials_flagged(self):
        """Test PFAS-containing materials are flagged."""
        pvdf = Material.PVDF
        assert pvdf.pfas_containing is True
        assert pvdf.releases_toxins is True

    def test_recyclability_scores(self):
        """Test recyclability scores are in valid range."""
        for mat in Material.get_all():
            assert 0.0 <= mat.recyclability_score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
