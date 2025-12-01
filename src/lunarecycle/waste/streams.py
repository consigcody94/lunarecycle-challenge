"""
Waste stream definitions based on NASA LunaRecycle Challenge specifications.

Table 4 from the challenge rules defines 6 waste categories with 17 waste items.
This module provides the data structures and definitions for modeling these waste streams.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional


class WasteCategory(Enum):
    """
    Six waste categories defined in NASA LunaRecycle Challenge Table 4.

    Teams must choose one or more categories to recycle. Not required to
    recycle all items within a chosen category.
    """
    FOOD_PACKAGING = auto()      # Plastic films, foil pouches, retort packaging
    CLOTHING = auto()            # Cotton, synthetic fabrics
    FOAM_PACKING = auto()        # Zotek F30, protective foam materials
    HYGIENE_ITEMS = auto()       # Wipes, towels (dry, non-metabolic)
    SCIENCE_MATERIALS = auto()   # Experiment consumables, sample containers
    GENERAL_WASTE = auto()       # Tape, paper, filters, misc items


class DifficultyLevel(Enum):
    """Difficulty levels for waste items as defined in challenge scoring."""
    LEVEL_1 = 1  # Easiest to recycle
    LEVEL_2 = 2  # Moderate difficulty
    LEVEL_3 = 3  # Most difficult (e.g., Zotek foam)


@dataclass
class MaterialComposition:
    """Chemical/material composition of a waste item."""
    primary_material: str
    primary_percentage: float  # 0-100
    secondary_materials: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        total = self.primary_percentage + sum(self.secondary_materials.values())
        if not (99.0 <= total <= 101.0):  # Allow small rounding errors
            raise ValueError(f"Material composition must sum to 100%, got {total}%")


@dataclass
class WasteItem:
    """
    Individual waste item specification.

    Based on NASA LunaRecycle Challenge Table 4 - Eligible Trash Items.
    """
    name: str
    category: WasteCategory
    difficulty: DifficultyLevel

    # Physical properties
    mass_per_unit_kg: float
    volume_per_unit_m3: float
    density_kg_m3: float

    # Material composition
    composition: MaterialComposition

    # Generation rate (units per crew member per day)
    generation_rate_per_crew_day: float

    # Processing characteristics
    melting_point_c: Optional[float] = None
    decomposition_temp_c: Optional[float] = None
    heating_value_mj_kg: Optional[float] = None  # Energy content
    moisture_content_percent: float = 0.0

    # Commercial equivalent for testing
    commercial_equivalent: Optional[str] = None

    @property
    def daily_mass_4_crew(self) -> float:
        """Mass generated per day for a 4-person crew (kg)."""
        return self.mass_per_unit_kg * self.generation_rate_per_crew_day * 4

    @property
    def annual_mass_4_crew(self) -> float:
        """Mass generated per year for a 4-person crew (kg)."""
        return self.daily_mass_4_crew * 365


class WasteStream:
    """
    Pre-defined waste streams based on NASA LunaRecycle specifications.

    These represent the standard waste items that teams can choose to recycle.
    Data derived from ISS operations and NASA research.
    """

    # === FOOD PACKAGING (Category 1) ===
    FOOD_PACKAGING_FILM = WasteItem(
        name="Food Packaging Film",
        category=WasteCategory.FOOD_PACKAGING,
        difficulty=DifficultyLevel.LEVEL_1,
        mass_per_unit_kg=0.015,
        volume_per_unit_m3=0.0001,
        density_kg_m3=150.0,
        composition=MaterialComposition(
            primary_material="LDPE",
            primary_percentage=70.0,
            secondary_materials={"Aluminum": 20.0, "PET": 10.0}
        ),
        generation_rate_per_crew_day=3.0,
        melting_point_c=120.0,
        decomposition_temp_c=350.0,
        heating_value_mj_kg=46.0,
        commercial_equivalent="Multi-layer food pouch"
    )

    RETORT_POUCH = WasteItem(
        name="Retort Pouch",
        category=WasteCategory.FOOD_PACKAGING,
        difficulty=DifficultyLevel.LEVEL_2,
        mass_per_unit_kg=0.025,
        volume_per_unit_m3=0.00015,
        density_kg_m3=166.7,
        composition=MaterialComposition(
            primary_material="PET",
            primary_percentage=40.0,
            secondary_materials={"Aluminum": 35.0, "PP": 25.0}
        ),
        generation_rate_per_crew_day=2.0,
        melting_point_c=260.0,
        decomposition_temp_c=400.0,
        heating_value_mj_kg=35.0,
        commercial_equivalent="Rehydratable Pouch"
    )

    BEVERAGE_CONTAINER = WasteItem(
        name="Beverage Container",
        category=WasteCategory.FOOD_PACKAGING,
        difficulty=DifficultyLevel.LEVEL_1,
        mass_per_unit_kg=0.008,
        volume_per_unit_m3=0.00005,
        density_kg_m3=160.0,
        composition=MaterialComposition(
            primary_material="HDPE",
            primary_percentage=90.0,
            secondary_materials={"Additives": 10.0}
        ),
        generation_rate_per_crew_day=2.5,
        melting_point_c=130.0,
        decomposition_temp_c=380.0,
        heating_value_mj_kg=44.0,
        commercial_equivalent="PE dropper bottle"
    )

    # === CLOTHING (Category 2) ===
    COTTON_CLOTHING = WasteItem(
        name="Cotton Clothing",
        category=WasteCategory.CLOTHING,
        difficulty=DifficultyLevel.LEVEL_2,
        mass_per_unit_kg=0.150,
        volume_per_unit_m3=0.001,
        density_kg_m3=150.0,
        composition=MaterialComposition(
            primary_material="Cotton",
            primary_percentage=95.0,
            secondary_materials={"Elastane": 5.0}
        ),
        generation_rate_per_crew_day=0.3,  # Changed every ~3-4 days
        decomposition_temp_c=350.0,
        heating_value_mj_kg=17.0,
        moisture_content_percent=8.0,
        commercial_equivalent="Cotton t-shirt"
    )

    SYNTHETIC_CLOTHING = WasteItem(
        name="Synthetic Clothing",
        category=WasteCategory.CLOTHING,
        difficulty=DifficultyLevel.LEVEL_2,
        mass_per_unit_kg=0.120,
        volume_per_unit_m3=0.0008,
        density_kg_m3=150.0,
        composition=MaterialComposition(
            primary_material="Polyester",
            primary_percentage=85.0,
            secondary_materials={"Nylon": 10.0, "Elastane": 5.0}
        ),
        generation_rate_per_crew_day=0.25,
        melting_point_c=260.0,
        decomposition_temp_c=400.0,
        heating_value_mj_kg=23.0,
        commercial_equivalent="Polyester athletic wear"
    )

    # === FOAM/PACKING (Category 3) ===
    ZOTEK_FOAM = WasteItem(
        name="Zotek F30 Foam",
        category=WasteCategory.FOAM_PACKING,
        difficulty=DifficultyLevel.LEVEL_3,  # Hardest to recycle
        mass_per_unit_kg=0.050,
        volume_per_unit_m3=0.002,
        density_kg_m3=25.0,  # Very low density foam
        composition=MaterialComposition(
            primary_material="PVDF",  # Polyvinylidene fluoride
            primary_percentage=100.0,
        ),
        generation_rate_per_crew_day=0.5,
        melting_point_c=170.0,
        decomposition_temp_c=450.0,
        heating_value_mj_kg=13.0,
        commercial_equivalent="Zotek F30"
    )

    PE_FOAM = WasteItem(
        name="PE Foam Packaging",
        category=WasteCategory.FOAM_PACKING,
        difficulty=DifficultyLevel.LEVEL_2,
        mass_per_unit_kg=0.030,
        volume_per_unit_m3=0.001,
        density_kg_m3=30.0,
        composition=MaterialComposition(
            primary_material="PE",
            primary_percentage=98.0,
            secondary_materials={"Additives": 2.0}
        ),
        generation_rate_per_crew_day=0.8,
        melting_point_c=115.0,
        decomposition_temp_c=350.0,
        heating_value_mj_kg=46.0,
        commercial_equivalent="Polyethylene foam sheet"
    )

    # === HYGIENE ITEMS (Category 4) ===
    CLEANING_WIPES = WasteItem(
        name="Cleaning Wipes",
        category=WasteCategory.HYGIENE_ITEMS,
        difficulty=DifficultyLevel.LEVEL_1,
        mass_per_unit_kg=0.010,
        volume_per_unit_m3=0.00003,
        density_kg_m3=333.0,
        composition=MaterialComposition(
            primary_material="Polypropylene",
            primary_percentage=70.0,
            secondary_materials={"Cellulose": 30.0}
        ),
        generation_rate_per_crew_day=5.0,
        decomposition_temp_c=350.0,
        heating_value_mj_kg=20.0,
        moisture_content_percent=5.0,  # Dry wipes assumed
        commercial_equivalent="Dry cleaning wipe"
    )

    TOWELS = WasteItem(
        name="Towels",
        category=WasteCategory.HYGIENE_ITEMS,
        difficulty=DifficultyLevel.LEVEL_1,
        mass_per_unit_kg=0.080,
        volume_per_unit_m3=0.0003,
        density_kg_m3=266.7,
        composition=MaterialComposition(
            primary_material="Cotton",
            primary_percentage=80.0,
            secondary_materials={"Polyester": 20.0}
        ),
        generation_rate_per_crew_day=0.5,
        decomposition_temp_c=350.0,
        heating_value_mj_kg=17.0,
        commercial_equivalent="Cotton-blend towel"
    )

    # === SCIENCE MATERIALS (Category 5) ===
    SAMPLE_CONTAINERS = WasteItem(
        name="Sample Containers",
        category=WasteCategory.SCIENCE_MATERIALS,
        difficulty=DifficultyLevel.LEVEL_1,
        mass_per_unit_kg=0.020,
        volume_per_unit_m3=0.00005,
        density_kg_m3=400.0,
        composition=MaterialComposition(
            primary_material="PP",
            primary_percentage=95.0,
            secondary_materials={"Silicone": 5.0}
        ),
        generation_rate_per_crew_day=0.3,
        melting_point_c=160.0,
        decomposition_temp_c=380.0,
        heating_value_mj_kg=44.0,
        commercial_equivalent="Polypropylene vial"
    )

    EXPERIMENT_CONSUMABLES = WasteItem(
        name="Experiment Consumables",
        category=WasteCategory.SCIENCE_MATERIALS,
        difficulty=DifficultyLevel.LEVEL_2,
        mass_per_unit_kg=0.035,
        volume_per_unit_m3=0.0001,
        density_kg_m3=350.0,
        composition=MaterialComposition(
            primary_material="Mixed Plastics",
            primary_percentage=60.0,
            secondary_materials={"Paper": 25.0, "Metal": 15.0}
        ),
        generation_rate_per_crew_day=0.4,
        decomposition_temp_c=400.0,
        heating_value_mj_kg=25.0,
        commercial_equivalent="Lab consumables mix"
    )

    # === GENERAL WASTE (Category 6) ===
    TAPE = WasteItem(
        name="Tape",
        category=WasteCategory.GENERAL_WASTE,
        difficulty=DifficultyLevel.LEVEL_1,
        mass_per_unit_kg=0.005,
        volume_per_unit_m3=0.00001,
        density_kg_m3=500.0,
        composition=MaterialComposition(
            primary_material="PP",
            primary_percentage=60.0,
            secondary_materials={"Adhesive": 40.0}
        ),
        generation_rate_per_crew_day=1.0,
        decomposition_temp_c=350.0,
        heating_value_mj_kg=30.0,
        commercial_equivalent="Packing tape"
    )

    PAPER = WasteItem(
        name="Paper Products",
        category=WasteCategory.GENERAL_WASTE,
        difficulty=DifficultyLevel.LEVEL_1,
        mass_per_unit_kg=0.010,
        volume_per_unit_m3=0.00005,
        density_kg_m3=200.0,
        composition=MaterialComposition(
            primary_material="Cellulose",
            primary_percentage=90.0,
            secondary_materials={"Additives": 10.0}
        ),
        generation_rate_per_crew_day=0.5,
        decomposition_temp_c=250.0,
        heating_value_mj_kg=17.0,
        commercial_equivalent="Office paper"
    )

    FILTERS = WasteItem(
        name="Filters",
        category=WasteCategory.GENERAL_WASTE,
        difficulty=DifficultyLevel.LEVEL_2,
        mass_per_unit_kg=0.100,
        volume_per_unit_m3=0.0005,
        density_kg_m3=200.0,
        composition=MaterialComposition(
            primary_material="Activated Carbon",
            primary_percentage=50.0,
            secondary_materials={"PP": 30.0, "Cellulose": 20.0}
        ),
        generation_rate_per_crew_day=0.1,  # Changed less frequently
        decomposition_temp_c=450.0,
        heating_value_mj_kg=25.0,
        commercial_equivalent="HEPA/carbon filter"
    )

    @classmethod
    def get_all_items(cls) -> list[WasteItem]:
        """Get all defined waste items."""
        return [
            cls.FOOD_PACKAGING_FILM,
            cls.RETORT_POUCH,
            cls.BEVERAGE_CONTAINER,
            cls.COTTON_CLOTHING,
            cls.SYNTHETIC_CLOTHING,
            cls.ZOTEK_FOAM,
            cls.PE_FOAM,
            cls.CLEANING_WIPES,
            cls.TOWELS,
            cls.SAMPLE_CONTAINERS,
            cls.EXPERIMENT_CONSUMABLES,
            cls.TAPE,
            cls.PAPER,
            cls.FILTERS,
        ]

    @classmethod
    def get_by_category(cls, category: WasteCategory) -> list[WasteItem]:
        """Get all waste items in a specific category."""
        return [item for item in cls.get_all_items() if item.category == category]

    @classmethod
    def get_total_daily_mass_4_crew(cls) -> float:
        """Calculate total daily waste mass for 4-person crew (kg)."""
        return sum(item.daily_mass_4_crew for item in cls.get_all_items())

    @classmethod
    def get_total_annual_mass_4_crew(cls) -> float:
        """Calculate total annual waste mass for 4-person crew (kg)."""
        return sum(item.annual_mass_4_crew for item in cls.get_all_items())


# Convenience function to display waste stream summary
def print_waste_summary():
    """Print a summary of all waste streams."""
    print("\n=== NASA LunaRecycle Waste Stream Summary ===\n")

    total_daily = 0.0
    for category in WasteCategory:
        items = WasteStream.get_by_category(category)
        if items:
            print(f"\n{category.name}:")
            cat_daily = 0.0
            for item in items:
                daily = item.daily_mass_4_crew
                cat_daily += daily
                print(f"  - {item.name}: {daily:.3f} kg/day (Difficulty: {item.difficulty.value})")
            print(f"  Category Total: {cat_daily:.3f} kg/day")
            total_daily += cat_daily

    print(f"\n{'='*50}")
    print(f"TOTAL DAILY (4-crew): {total_daily:.2f} kg/day")
    print(f"TOTAL ANNUAL (4-crew): {total_daily * 365:.0f} kg/year")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    print_waste_summary()
