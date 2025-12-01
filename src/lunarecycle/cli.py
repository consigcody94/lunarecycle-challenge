"""
Command-line interface for LunaRecycle simulation.

Usage:
    lunarecycle run [options]
    lunarecycle compare [options]
    lunarecycle waste-summary
"""

import argparse
import sys
from pathlib import Path

from lunarecycle import __version__
from lunarecycle.simulation.engine import Simulation, quick_simulation
from lunarecycle.waste.streams import print_waste_summary
from lunarecycle.analysis.reports import (
    generate_summary_report,
    export_results_csv,
    compare_technologies,
    print_technology_comparison,
)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="lunarecycle",
        description="NASA LunaRecycle Challenge - Lunar Waste Recycling Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    lunarecycle run --days 365 --technology hybrid
    lunarecycle run --days 180 --location mars_habitat
    lunarecycle compare --days 365
    lunarecycle waste-summary
        """
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"lunarecycle {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run simulation command
    run_parser = subparsers.add_parser("run", help="Run a simulation")
    run_parser.add_argument(
        "--days", "-d",
        type=int,
        default=365,
        help="Mission duration in days (default: 365)"
    )
    run_parser.add_argument(
        "--crew", "-c",
        type=int,
        default=4,
        help="Crew size (default: 4)"
    )
    run_parser.add_argument(
        "--location", "-l",
        type=str,
        default="lunar_habitat",
        choices=["lunar_habitat", "lunar_surface", "mars_habitat", "mars_surface"],
        help="Operating location (default: lunar_habitat)"
    )
    run_parser.add_argument(
        "--technology", "-t",
        type=str,
        default="hybrid",
        choices=["pyrolysis", "melt_extrusion", "plasma", "hybrid", "compaction"],
        help="Recycling technology (default: hybrid)"
    )
    run_parser.add_argument(
        "--frequency", "-f",
        type=int,
        default=7,
        help="Processing frequency in days (default: 7)"
    )
    run_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path for report"
    )
    run_parser.add_argument(
        "--csv",
        type=str,
        help="Export daily metrics to CSV file"
    )
    run_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Compare technologies command
    compare_parser = subparsers.add_parser("compare", help="Compare recycling technologies")
    compare_parser.add_argument(
        "--days", "-d",
        type=int,
        default=365,
        help="Mission duration for comparison (default: 365)"
    )
    compare_parser.add_argument(
        "--technologies", "-t",
        type=str,
        nargs="+",
        default=["pyrolysis", "melt_extrusion", "plasma", "hybrid"],
        help="Technologies to compare"
    )

    # Waste summary command
    subparsers.add_parser("waste-summary", help="Display waste stream summary")

    # Parse arguments
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    # Execute commands
    if args.command == "run":
        return cmd_run(args)
    elif args.command == "compare":
        return cmd_compare(args)
    elif args.command == "waste-summary":
        print_waste_summary()
        return 0

    return 0


def cmd_run(args):
    """Run simulation command."""
    print(f"\n🚀 LunaRecycle Simulation v{__version__}")
    print(f"   Location: {args.location}")
    print(f"   Duration: {args.days} days")
    print(f"   Crew: {args.crew}")
    print(f"   Technology: {args.technology}")
    print("\nRunning simulation...")

    # Create and run simulation
    sim = Simulation(
        crew_size=args.crew,
        mission_duration_days=args.days,
        location=args.location,
        recycling_technology=args.technology,
        processing_frequency_days=args.frequency
    )

    results = sim.run()

    # Output results
    if args.json:
        print(results.to_json())
    else:
        results.print_summary()

    # Save report if requested
    if args.output:
        report = generate_summary_report(results, Path(args.output))
        print(f"\nReport saved to: {args.output}")

    # Export CSV if requested
    if args.csv:
        export_results_csv(results, Path(args.csv))

    return 0


def cmd_compare(args):
    """Compare technologies command."""
    print(f"\n🔬 Comparing Recycling Technologies")
    print(f"   Duration: {args.days} days")
    print(f"   Technologies: {', '.join(args.technologies)}")
    print("\nRunning comparisons...")

    comparison = compare_technologies(
        days=args.days,
        technologies=args.technologies
    )

    print_technology_comparison(comparison)

    return 0


if __name__ == "__main__":
    sys.exit(main())
