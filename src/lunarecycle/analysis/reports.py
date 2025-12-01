"""
Analysis and reporting tools for LunaRecycle simulations.

Generates reports, charts, and exports for simulation results.
"""

import csv
from pathlib import Path
from typing import Optional
from datetime import datetime

from lunarecycle.simulation.engine import SimulationResults


def generate_summary_report(results: SimulationResults, output_path: Optional[Path] = None) -> str:
    """
    Generate a text summary report of simulation results.

    Args:
        results: SimulationResults from a simulation run
        output_path: Optional path to save the report

    Returns:
        Report text
    """
    report_lines = [
        "=" * 80,
        "LUNARECYCLE SIMULATION REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80,
        "",
        "MISSION CONFIGURATION",
        "-" * 40,
        f"Duration:        {results.config.mission_duration_days} days",
        f"Crew Size:       {results.config.crew_size}",
        f"Location:        {results.config.location}",
        f"Technology:      {results.config.recycling_technology}",
        f"Processing Freq: Every {results.config.processing_frequency_days} days",
        "",
        "ENVIRONMENT",
        "-" * 40,
        f"Gravity:         {results.environment.gravity_m_s2:.2f} m/s²",
        f"Pressure:        {results.environment.atmosphere.pressure_kpa:.1f} kPa",
        f"Temperature:     {results.environment.thermal.avg_temp_c:.1f}°C (avg)",
        f"Power Available: {results.environment.power.avg_power_kw:.1f} kW (avg)",
        "",
        "MASS BALANCE",
        "-" * 40,
        f"Total Waste Generated:  {results.total_waste_generated_kg:,.1f} kg",
        f"Total Waste Processed:  {results.total_waste_processed_kg:,.1f} kg",
        f"Total Products Created: {results.total_products_kg:,.1f} kg",
        f"Total Residue:          {results.total_residue_kg:,.1f} kg",
        f"Unprocessed Waste:      {results.total_waste_generated_kg - results.total_waste_processed_kg:,.1f} kg",
        "",
        f"Recycling Rate:    {results.recycling_rate * 100:.1f}%",
        f"Mass Recovery:     {results.mass_recovery_rate * 100:.1f}%",
        "",
        "ENERGY BALANCE",
        "-" * 40,
        f"Energy Consumed:  {results.total_energy_consumed_kwh:,.1f} kWh",
        f"Energy Recovered: {results.total_energy_recovered_kwh:,.1f} kWh",
        f"Net Energy:       {results.net_energy_kwh:,.1f} kWh",
        "",
        "PRODUCTS PRODUCED",
        "-" * 40,
    ]

    for product, mass in sorted(results.products_by_type.items(), key=lambda x: -x[1]):
        pct = (mass / results.total_products_kg * 100) if results.total_products_kg > 0 else 0
        report_lines.append(f"  {product:20s}: {mass:,.1f} kg ({pct:.1f}%)")

    report_lines.extend([
        "",
        "CHALLENGE SCORING",
        "-" * 40,
    ])

    for criterion, score in results.score_breakdown.items():
        report_lines.append(f"  {criterion:25s}: {score:.1f}")

    report_lines.extend([
        f"  {'TOTAL SCORE':25s}: {results.total_score:.1f}",
        "",
        "DAILY STATISTICS",
        "-" * 40,
        f"Avg Daily Waste:     {results.total_waste_generated_kg / results.config.mission_duration_days:.2f} kg/day",
        f"Avg Daily Products:  {results.total_products_kg / results.config.mission_duration_days:.2f} kg/day",
        f"Avg Daily Energy:    {results.total_energy_consumed_kwh / results.config.mission_duration_days:.2f} kWh/day",
        "",
        "=" * 80,
    ])

    report_text = "\n".join(report_lines)

    if output_path:
        output_path.write_text(report_text)

    return report_text


def generate_mass_balance_chart(results: SimulationResults, output_path: Optional[Path] = None):
    """
    Generate a mass balance visualization.

    Uses matplotlib if available, otherwise creates ASCII chart.
    """
    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Chart 1: Mass flow Sankey-style bar
        categories = ['Generated', 'Processed', 'Products', 'Residue']
        values = [
            results.total_waste_generated_kg,
            results.total_waste_processed_kg,
            results.total_products_kg,
            results.total_residue_kg
        ]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

        axes[0].barh(categories, values, color=colors)
        axes[0].set_xlabel('Mass (kg)')
        axes[0].set_title('Mass Balance Overview')
        for i, v in enumerate(values):
            axes[0].text(v + 10, i, f'{v:.0f} kg', va='center')

        # Chart 2: Products breakdown pie chart
        if results.products_by_type:
            products = list(results.products_by_type.keys())
            masses = list(results.products_by_type.values())
            axes[1].pie(masses, labels=products, autopct='%1.1f%%', startangle=90)
            axes[1].set_title('Products Breakdown')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    except ImportError:
        # Fallback to ASCII chart
        print("\nMASS BALANCE (ASCII Chart)")
        print("-" * 50)
        max_val = max(results.total_waste_generated_kg, results.total_waste_processed_kg)
        scale = 40 / max_val if max_val > 0 else 1

        data = [
            ("Generated", results.total_waste_generated_kg),
            ("Processed", results.total_waste_processed_kg),
            ("Products", results.total_products_kg),
            ("Residue", results.total_residue_kg),
        ]

        for label, value in data:
            bar_len = int(value * scale)
            bar = "█" * bar_len
            print(f"{label:12s} |{bar} {value:.0f} kg")


def generate_energy_chart(results: SimulationResults, output_path: Optional[Path] = None):
    """Generate energy consumption/recovery visualization."""
    try:
        import matplotlib.pyplot as plt

        # Time series of cumulative energy
        days = [m.day for m in results.daily_metrics]
        cumulative_consumed = []
        cumulative_recovered = []
        running_consumed = 0
        running_recovered = 0

        for m in results.daily_metrics:
            running_consumed += m.energy_consumed_kwh
            running_recovered += m.energy_recovered_kwh
            cumulative_consumed.append(running_consumed)
            cumulative_recovered.append(running_recovered)

        plt.figure(figsize=(12, 6))
        plt.plot(days, cumulative_consumed, label='Energy Consumed', color='red', linewidth=2)
        plt.plot(days, cumulative_recovered, label='Energy Recovered', color='green', linewidth=2)
        plt.fill_between(days, cumulative_consumed, alpha=0.3, color='red')
        plt.fill_between(days, cumulative_recovered, alpha=0.3, color='green')

        plt.xlabel('Mission Day')
        plt.ylabel('Cumulative Energy (kWh)')
        plt.title('Energy Balance Over Mission Duration')
        plt.legend()
        plt.grid(True, alpha=0.3)

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    except ImportError:
        print("\nENERGY BALANCE (ASCII)")
        print("-" * 50)
        print(f"Energy Consumed:  {results.total_energy_consumed_kwh:.1f} kWh")
        print(f"Energy Recovered: {results.total_energy_recovered_kwh:.1f} kWh")
        print(f"Net Energy:       {results.net_energy_kwh:.1f} kWh")


def export_results_csv(results: SimulationResults, output_path: Path):
    """
    Export daily metrics to CSV file.

    Args:
        results: SimulationResults to export
        output_path: Path for output CSV file
    """
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Day',
            'Date',
            'Waste_Generated_kg',
            'Waste_Processed_kg',
            'Waste_Accumulated_kg',
            'Products_Produced_kg',
            'Energy_Consumed_kWh',
            'Energy_Recovered_kWh',
            'Net_Energy_kWh'
        ])

        # Data rows
        for m in results.daily_metrics:
            writer.writerow([
                m.day,
                m.date.strftime('%Y-%m-%d'),
                f'{m.waste_generated_kg:.3f}',
                f'{m.waste_processed_kg:.3f}',
                f'{m.waste_accumulated_kg:.3f}',
                f'{m.products_produced_kg:.3f}',
                f'{m.energy_consumed_kwh:.3f}',
                f'{m.energy_recovered_kwh:.3f}',
                f'{m.energy_recovered_kwh - m.energy_consumed_kwh:.3f}'
            ])

    print(f"Results exported to: {output_path}")


def compare_technologies(
    days: int = 365,
    technologies: Optional[list[str]] = None
) -> dict:
    """
    Compare different recycling technologies.

    Args:
        days: Simulation duration
        technologies: List of technology names to compare

    Returns:
        Dictionary with comparison results
    """
    from lunarecycle.simulation.engine import Simulation

    if technologies is None:
        technologies = ["pyrolysis", "melt_extrusion", "plasma", "hybrid"]

    comparison = {}

    for tech in technologies:
        sim = Simulation(
            crew_size=4,
            mission_duration_days=days,
            location="lunar_habitat",
            recycling_technology=tech
        )
        results = sim.run()

        comparison[tech] = {
            "recycling_rate": results.recycling_rate,
            "mass_recovery": results.mass_recovery_rate,
            "net_energy_kwh": results.net_energy_kwh,
            "total_score": results.total_score,
            "products": results.products_by_type
        }

    return comparison


def print_technology_comparison(comparison: dict):
    """Print formatted technology comparison."""
    print("\n" + "=" * 80)
    print("TECHNOLOGY COMPARISON")
    print("=" * 80)

    headers = ["Technology", "Recycling %", "Recovery %", "Net Energy", "Score"]
    row_format = "{:20s} {:>12s} {:>12s} {:>12s} {:>8s}"

    print(row_format.format(*headers))
    print("-" * 80)

    for tech, data in comparison.items():
        print(row_format.format(
            tech.upper(),
            f"{data['recycling_rate']*100:.1f}%",
            f"{data['mass_recovery']*100:.1f}%",
            f"{data['net_energy_kwh']:.0f} kWh",
            f"{data['total_score']:.1f}"
        ))

    print("=" * 80)
