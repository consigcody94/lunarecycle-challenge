"""
LunaRecycle - NASA LunaRecycle Challenge Simulation System

A comprehensive simulation framework for modeling waste management and recycling
processes for long-duration lunar missions.
"""

__version__ = "0.1.0"

from lunarecycle.waste.streams import WasteStream, WasteCategory, WasteItem
from lunarecycle.waste.inventory import WasteInventory
from lunarecycle.recycling.systems import RecyclingSystem, RecyclingTechnology
from lunarecycle.recycling.processes import ProcessingResult
from lunarecycle.environment.lunar import LunarEnvironment
from lunarecycle.simulation.engine import Simulation, SimulationResults

__all__ = [
    # Version
    "__version__",
    # Waste
    "WasteStream",
    "WasteCategory",
    "WasteItem",
    "WasteInventory",
    # Recycling
    "RecyclingSystem",
    "RecyclingTechnology",
    "ProcessingResult",
    # Environment
    "LunarEnvironment",
    # Simulation
    "Simulation",
    "SimulationResults",
]
