#!/usr/bin/env python3
"""
Basic LunaRecycle Simulation Example

This example demonstrates how to:
1. Set up a lunar mission waste simulation
2. Configure recycling systems
3. Run the simulation
4. Analyze results

Run with: python examples/basic_simulation.py
"""

from lunarecycle import (
    Simulation,
    WasteStream,
    WasteCategory,
    RecyclingSystem,
    RecyclingTechnology,
)
from lunarecycle.recycling.systems import create_system
from lunarecycle.analysis.reports import (
    generate_summary_report,
    compare_technologies,
    print_technology_comparison,
)


def basic_example():
    """Run a basic simulation with default settings."""
    print("\n" + "=" * 60)
    print("BASIC SIMULATION EXAMPLE")
    print("=" * 60)

    # Create simulation for a 1-year lunar habitat mission
    sim = Simulation(
        crew_size=4,
        mission_duration_days=365,
        location="lunar_habitat"
    )

    # Run with default hybrid recycling system
    results = sim.run()

    # Print summary
    results.print_summary()

    return results


def custom_system_example():
    """Example with custom recycling system configuration."""
    print("\n" + "=" * 60)
    print("CUSTOM SYSTEM EXAMPLE")
    print("=" * 60)

    # Create simulation
    sim = Simulation(
        crew_size=4,
        mission_duration_days=180,  # 6 months
        location="lunar_habitat",
        processing_frequency_days=3,  # Process every 3 days
    )

    # Create custom pyrolysis-focused system
    system = create_system("pyrolysis", name="PyroLuna-1")

    # Set the system
    sim.set_recycling_system(system)

    # Run simulation
    results = sim.run()
    results.print_summary()

    return results


def selective_waste_example():
    """Example processing only specific waste categories."""
    print("\n" + "=" * 60)
    print("SELECTIVE WASTE PROCESSING EXAMPLE")
    print("=" * 60)

    # Create simulation targeting only food packaging and clothing
    sim = Simulation(
        crew_size=4,
        mission_duration_days=90,
        location="lunar_habitat",
        waste_categories=[
            WasteCategory.FOOD_PACKAGING,
            WasteCategory.CLOTHING,
        ]
    )

    results = sim.run()
    results.print_summary()

    return results


def mars_mission_example():
    """Example simulation for Mars habitat."""
    print("\n" + "=" * 60)
    print("MARS MISSION EXAMPLE")
    print("=" * 60)

    # Mars mission - no resupply, everything must be recycled
    sim = Simulation(
        crew_size=4,
        mission_duration_days=500,  # ~1.4 year mission
        location="mars_habitat",
        recycling_technology="hybrid",
        processing_frequency_days=5,
    )

    results = sim.run()
    results.print_summary()

    print("\n⚠️  Note: Mars missions have no resupply capability!")
    print(f"   Unprocessed waste: {results.total_waste_generated_kg - results.total_waste_processed_kg:.1f} kg")

    return results


def technology_comparison_example():
    """Compare different recycling technologies."""
    print("\n" + "=" * 60)
    print("TECHNOLOGY COMPARISON")
    print("=" * 60)

    comparison = compare_technologies(
        days=365,
        technologies=["pyrolysis", "melt_extrusion", "plasma", "hybrid"]
    )

    print_technology_comparison(comparison)


def waste_summary_example():
    """Display waste stream information."""
    print("\n" + "=" * 60)
    print("WASTE STREAM SUMMARY")
    print("=" * 60)

    from lunarecycle.waste.streams import print_waste_summary
    print_waste_summary()


def main():
    """Run all examples."""
    print("\n" + "🚀" * 20)
    print("LUNARECYCLE SIMULATION EXAMPLES")
    print("NASA LunaRecycle Challenge - Digital Twin Simulation")
    print("🚀" * 20)

    # Run examples
    waste_summary_example()
    basic_example()
    custom_system_example()
    selective_waste_example()
    technology_comparison_example()
    mars_mission_example()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
