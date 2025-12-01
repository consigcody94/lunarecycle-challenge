"""
ARTEMIS-R (Advanced Recycling Technology for Extraterrestrial Material Integration System - Recycler)

This module implements the digital twin for the ARTEMIS-R physical prototype,
a hybrid solar-thermal processing system for lunar waste recycling.
"""

from .system import ARTEMISSystem
from .modules import (
    ThermalProcessor,
    MeltExtruder,
    MechanicalShredder,
    CompositePress,
    InputHopper,
)
from .control import ARTEMISController, OperatingMode
from .digital_twin import DigitalTwin

__all__ = [
    "ARTEMISSystem",
    "ThermalProcessor",
    "MeltExtruder",
    "MechanicalShredder",
    "CompositePress",
    "InputHopper",
    "ARTEMISController",
    "OperatingMode",
    "DigitalTwin",
]
