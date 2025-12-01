"""
Lunar and planetary environment parameters.

Based on NASA LunaRecycle Challenge Table 5 - Planetary Environmental Conditions.
Defines environmental constraints for lunar and Mars surface operations.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class Location(Enum):
    """Operating location for recycling system."""
    LUNAR_SURFACE = auto()
    LUNAR_HABITAT = auto()
    MARS_SURFACE = auto()
    MARS_HABITAT = auto()
    LEO_STATION = auto()  # Low Earth Orbit (ISS-like)


@dataclass
class AtmosphericConditions:
    """Atmospheric parameters for a location."""
    pressure_kpa: float
    composition: dict[str, float]  # Gas: percentage
    oxygen_partial_pressure_kpa: float = 21.0
    humidity_percent: float = 40.0


@dataclass
class ThermalConditions:
    """Temperature and thermal parameters."""
    min_temp_c: float
    max_temp_c: float
    avg_temp_c: float
    thermal_cycling: bool = True  # Day/night cycling


@dataclass
class RadiationEnvironment:
    """Radiation parameters."""
    galactic_cosmic_ray_msv_year: float
    solar_particle_event_risk: str  # "low", "medium", "high"
    shielding_available: bool = True


@dataclass
class PowerAvailability:
    """Power system parameters."""
    avg_power_kw: float
    peak_power_kw: float
    solar_available_hours_day: float
    storage_capacity_kwh: float


@dataclass
class EnvironmentParameters:
    """Complete environment specification."""
    location: Location
    gravity_m_s2: float
    atmosphere: AtmosphericConditions
    thermal: ThermalConditions
    radiation: RadiationEnvironment
    power: PowerAvailability

    # Operational constraints
    crew_available_hours_day: float = 4.0  # Hours crew can dedicate to recycling
    eva_required: bool = False  # Whether EVA needed for operations
    resupply_interval_days: Optional[int] = None  # Days between resupply


class LunarEnvironment:
    """
    Lunar surface and habitat environment parameters.

    Based on NASA LunaRecycle Challenge specifications and
    Artemis mission planning data.
    """

    # Physical constants
    LUNAR_GRAVITY = 1.62  # m/s²
    EARTH_GRAVITY = 9.81  # m/s²
    GRAVITY_RATIO = LUNAR_GRAVITY / EARTH_GRAVITY  # ~0.165

    # Lunar day/night cycle
    LUNAR_DAY_HOURS = 354.4  # ~14.75 Earth days of sunlight
    LUNAR_NIGHT_HOURS = 354.4  # ~14.75 Earth days of darkness

    @classmethod
    def surface(cls) -> EnvironmentParameters:
        """
        Lunar surface environment (outside habitat).

        Extreme conditions - exposed to vacuum and temperature swings.
        """
        return EnvironmentParameters(
            location=Location.LUNAR_SURFACE,
            gravity_m_s2=cls.LUNAR_GRAVITY,
            atmosphere=AtmosphericConditions(
                pressure_kpa=0.0,  # Vacuum
                composition={},
                oxygen_partial_pressure_kpa=0.0,
                humidity_percent=0.0
            ),
            thermal=ThermalConditions(
                min_temp_c=-173.0,  # Lunar night
                max_temp_c=127.0,   # Lunar day
                avg_temp_c=-20.0,
                thermal_cycling=True
            ),
            radiation=RadiationEnvironment(
                galactic_cosmic_ray_msv_year=380.0,
                solar_particle_event_risk="high",
                shielding_available=False
            ),
            power=PowerAvailability(
                avg_power_kw=5.0,
                peak_power_kw=15.0,
                solar_available_hours_day=12.0,  # Varies with location
                storage_capacity_kwh=100.0
            ),
            crew_available_hours_day=2.0,  # Limited EVA time
            eva_required=True,
            resupply_interval_days=180  # ~6 months
        )

    @classmethod
    def habitat(cls) -> EnvironmentParameters:
        """
        Pressurized lunar habitat environment.

        Controlled conditions - shirtsleeve environment.
        """
        return EnvironmentParameters(
            location=Location.LUNAR_HABITAT,
            gravity_m_s2=cls.LUNAR_GRAVITY,
            atmosphere=AtmosphericConditions(
                pressure_kpa=101.3,  # Earth-like
                composition={
                    "N2": 78.0,
                    "O2": 21.0,
                    "Ar": 0.9,
                    "CO2": 0.1
                },
                oxygen_partial_pressure_kpa=21.3,
                humidity_percent=45.0
            ),
            thermal=ThermalConditions(
                min_temp_c=18.0,
                max_temp_c=26.0,
                avg_temp_c=22.0,
                thermal_cycling=False  # Climate controlled
            ),
            radiation=RadiationEnvironment(
                galactic_cosmic_ray_msv_year=100.0,  # Reduced by shielding
                solar_particle_event_risk="medium",
                shielding_available=True
            ),
            power=PowerAvailability(
                avg_power_kw=10.0,
                peak_power_kw=25.0,
                solar_available_hours_day=12.0,
                storage_capacity_kwh=200.0
            ),
            crew_available_hours_day=4.0,
            eva_required=False,
            resupply_interval_days=180
        )

    @classmethod
    def get_processing_constraints(cls, location: Location) -> dict:
        """
        Get processing constraints for a location.

        Returns operational limits for recycling systems.
        """
        if location in (Location.LUNAR_SURFACE, Location.MARS_SURFACE):
            return {
                "max_operating_temp_c": 200.0,  # Equipment thermal limits
                "min_operating_temp_c": -40.0,
                "max_power_draw_kw": 5.0,
                "vacuum_compatible_required": True,
                "dust_mitigation_required": True,
                "autonomous_operation_required": True,
                "maintenance_interval_days": 30,
            }
        else:  # Habitat
            return {
                "max_operating_temp_c": 300.0,
                "min_operating_temp_c": 10.0,
                "max_power_draw_kw": 10.0,
                "vacuum_compatible_required": False,
                "dust_mitigation_required": False,
                "autonomous_operation_required": False,
                "maintenance_interval_days": 90,
            }


class MarsEnvironment:
    """
    Mars surface and habitat environment parameters.

    Based on NASA LunaRecycle Challenge Table 5 specifications.
    """

    # Physical constants
    MARS_GRAVITY = 3.72  # m/s²
    MARS_DAY_HOURS = 24.6  # Sol length

    @classmethod
    def surface(cls) -> EnvironmentParameters:
        """Mars surface environment (outside habitat)."""
        return EnvironmentParameters(
            location=Location.MARS_SURFACE,
            gravity_m_s2=cls.MARS_GRAVITY,
            atmosphere=AtmosphericConditions(
                pressure_kpa=0.636,  # ~0.6% of Earth
                composition={
                    "CO2": 95.3,
                    "N2": 2.7,
                    "Ar": 1.6,
                    "O2": 0.13,
                    "CO": 0.08
                },
                oxygen_partial_pressure_kpa=0.0008,
                humidity_percent=0.0
            ),
            thermal=ThermalConditions(
                min_temp_c=-125.0,  # Winter poles
                max_temp_c=20.0,    # Summer equator
                avg_temp_c=-60.0,
                thermal_cycling=True
            ),
            radiation=RadiationEnvironment(
                galactic_cosmic_ray_msv_year=250.0,
                solar_particle_event_risk="medium",
                shielding_available=False
            ),
            power=PowerAvailability(
                avg_power_kw=3.0,  # Reduced solar flux
                peak_power_kw=10.0,
                solar_available_hours_day=12.0,
                storage_capacity_kwh=150.0
            ),
            crew_available_hours_day=2.0,
            eva_required=True,
            resupply_interval_days=None  # No resupply possible
        )

    @classmethod
    def habitat(cls) -> EnvironmentParameters:
        """Mars pressurized habitat environment."""
        return EnvironmentParameters(
            location=Location.MARS_HABITAT,
            gravity_m_s2=cls.MARS_GRAVITY,
            atmosphere=AtmosphericConditions(
                pressure_kpa=101.3,
                composition={
                    "N2": 78.0,
                    "O2": 21.0,
                    "Ar": 0.9,
                    "CO2": 0.1
                },
                oxygen_partial_pressure_kpa=21.3,
                humidity_percent=40.0
            ),
            thermal=ThermalConditions(
                min_temp_c=18.0,
                max_temp_c=26.0,
                avg_temp_c=22.0,
                thermal_cycling=False
            ),
            radiation=RadiationEnvironment(
                galactic_cosmic_ray_msv_year=80.0,
                solar_particle_event_risk="low",
                shielding_available=True
            ),
            power=PowerAvailability(
                avg_power_kw=8.0,
                peak_power_kw=20.0,
                solar_available_hours_day=12.0,
                storage_capacity_kwh=300.0
            ),
            crew_available_hours_day=4.0,
            eva_required=False,
            resupply_interval_days=None
        )


def get_environment(location: str) -> EnvironmentParameters:
    """
    Factory function to get environment parameters.

    Args:
        location: String identifier ("lunar_surface", "lunar_habitat",
                  "mars_surface", "mars_habitat")

    Returns:
        EnvironmentParameters for the specified location
    """
    location_map = {
        "lunar_surface": LunarEnvironment.surface,
        "lunar_habitat": LunarEnvironment.habitat,
        "moon_surface": LunarEnvironment.surface,
        "moon_habitat": LunarEnvironment.habitat,
        "mars_surface": MarsEnvironment.surface,
        "mars_habitat": MarsEnvironment.habitat,
    }

    location_lower = location.lower().replace(" ", "_")
    if location_lower in location_map:
        return location_map[location_lower]()

    raise ValueError(f"Unknown location: {location}. "
                     f"Valid options: {list(location_map.keys())}")
