"""
Recycling process models for different technologies.

Models thermochemical and mechanical recycling processes for space waste.
Based on NASA research and industrial recycling data.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto

from lunarecycle.waste.streams import WasteItem, WasteCategory
from lunarecycle.waste.materials import Material


class ProductType(Enum):
    """Types of products from recycling processes."""

    SYNGAS = auto()  # CO, H2, CH4 mixture
    PYROLYSIS_OIL = auto()  # Liquid hydrocarbons
    CHAR = auto()  # Solid carbon residue
    WATER = auto()  # Recovered water
    FILAMENT = auto()  # 3D printing filament
    PELLETS = auto()  # Plastic pellets for molding
    COMPOSITE = auto()  # Reinforced composite material
    CARBON_FIBER = auto()  # Structured carbon
    METAL = auto()  # Recovered metals
    ASH = auto()  # Inert residue
    HEAT = auto()  # Thermal energy


@dataclass
class Product:
    """Output product from a recycling process."""

    product_type: ProductType
    mass_kg: float
    quality_score: float = 1.0  # 0-1, 1 = highest quality
    energy_content_mj: float = 0.0  # For fuels
    description: str = ""


@dataclass
class ProcessingResult:
    """Results from processing waste through a recycling system."""

    input_mass_kg: float
    input_waste_items: list[WasteItem]

    # Outputs
    products: list[Product] = field(default_factory=list)
    waste_residue_kg: float = 0.0

    # Performance metrics
    mass_recovery_rate: float = 0.0  # Products / Input
    energy_consumed_kwh: float = 0.0
    energy_recovered_kwh: float = 0.0
    processing_time_hours: float = 0.0
    water_consumed_kg: float = 0.0

    # Quality metrics
    contamination_level: float = 0.0  # 0-1
    toxins_released: bool = False
    microplastics_generated: bool = False

    @property
    def total_product_mass(self) -> float:
        return sum(p.mass_kg for p in self.products)

    @property
    def net_energy_kwh(self) -> float:
        return self.energy_recovered_kwh - self.energy_consumed_kwh

    @property
    def efficiency(self) -> float:
        """Overall mass efficiency (products / input)."""
        if self.input_mass_kg > 0:
            return self.total_product_mass / self.input_mass_kg
        return 0.0


class RecyclingProcess(ABC):
    """Abstract base class for recycling processes."""

    def __init__(self, name: str, max_capacity_kg_hr: float):
        self.name = name
        self.max_capacity_kg_hr = max_capacity_kg_hr

    @abstractmethod
    def can_process(self, waste_item: WasteItem) -> bool:
        """Check if this process can handle the given waste item."""
        pass

    @abstractmethod
    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """Process waste and return results."""
        pass

    @abstractmethod
    def get_energy_requirement(self, mass_kg: float) -> float:
        """Get energy requirement in kWh for processing given mass."""
        pass


class PyrolysisProcess(RecyclingProcess):
    """
    Pyrolysis recycling process.

    Thermal decomposition in absence of oxygen, converting polymers
    to syngas, oil, and char. Operating temperature: 400-700°C.

    Suitable for: Plastics, textiles, paper/cellulose
    Not suitable for: Metals, high-fluorine materials (PVDF)
    """

    def __init__(
        self,
        max_capacity_kg_hr: float = 2.0,
        operating_temp_c: float = 550.0,
        residence_time_min: float = 30.0,
    ):
        super().__init__("Pyrolysis", max_capacity_kg_hr)
        self.operating_temp_c = operating_temp_c
        self.residence_time_min = residence_time_min

        # Energy requirements (kWh per kg processed)
        self.specific_energy_kwh_kg = 1.5  # Based on literature

        # Acceptable categories
        self.acceptable_categories = {
            WasteCategory.FOOD_PACKAGING,
            WasteCategory.CLOTHING,
            WasteCategory.HYGIENE_ITEMS,
            WasteCategory.GENERAL_WASTE,
            WasteCategory.SCIENCE_MATERIALS,
        }

    def can_process(self, waste_item: WasteItem) -> bool:
        # Can process most organic materials except fluorinated foams
        if waste_item.category == WasteCategory.FOAM_PACKING:
            # Zotek F30 (PVDF) releases HF - not suitable
            if "PVDF" in waste_item.composition.primary_material:
                return False
        return waste_item.category in self.acceptable_categories

    def get_energy_requirement(self, mass_kg: float) -> float:
        return mass_kg * self.specific_energy_kwh_kg

    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """
        Process waste through pyrolysis.

        Products depend on input material composition.
        """
        total_input = sum(masses_kg)

        # Initialize product accumulators
        syngas_mass = 0.0
        oil_mass = 0.0
        char_mass = 0.0
        water_mass = 0.0
        metal_mass = 0.0
        energy_content = 0.0

        toxins = False
        microplastics = False

        for item, mass in zip(waste_items, masses_kg):
            if not self.can_process(item):
                continue

            # Get material properties for primary material
            mat = Material.get_by_name(item.composition.primary_material)
            if mat is None:
                # Default yields for unknown materials
                syngas_mass += mass * 0.20
                oil_mass += mass * 0.50
                char_mass += mass * 0.25
                water_mass += mass * 0.05
            else:
                # Use material-specific pyrolysis yields
                syngas_mass += mass * (mat.pyrolysis.syngas_yield_percent / 100)
                oil_mass += mass * (mat.pyrolysis.oil_yield_percent / 100)
                char_mass += mass * (mat.pyrolysis.char_yield_percent / 100)
                water_mass += mass * (mat.pyrolysis.water_yield_percent / 100)

                # Energy content from syngas and oil
                energy_content += mass * mat.heating_value_mj_kg * 0.6  # ~60% recovery

                if mat.releases_toxins:
                    toxins = True
                if mat.creates_microplastics:
                    # Pyrolysis should destroy microplastics at high temp
                    pass

            # Handle aluminum in multi-layer packaging
            if "Aluminum" in item.composition.secondary_materials:
                al_fraction = item.composition.secondary_materials["Aluminum"] / 100
                metal_mass += mass * al_fraction

        # Build product list
        products = []
        if syngas_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.SYNGAS,
                    mass_kg=syngas_mass,
                    quality_score=0.85,
                    energy_content_mj=energy_content * 0.4,
                    description="Synthesis gas (CO, H2, CH4)",
                )
            )
        if oil_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.PYROLYSIS_OIL,
                    mass_kg=oil_mass,
                    quality_score=0.7,
                    energy_content_mj=energy_content * 0.5,
                    description="Pyrolysis oil (liquid hydrocarbons)",
                )
            )
        if char_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.CHAR,
                    mass_kg=char_mass,
                    quality_score=0.9,
                    energy_content_mj=energy_content * 0.1,
                    description="Biochar/carbon residue",
                )
            )
        if water_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.WATER,
                    mass_kg=water_mass,
                    quality_score=0.6,  # Needs purification
                    description="Recovered water (requires treatment)",
                )
            )
        if metal_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.METAL,
                    mass_kg=metal_mass,
                    quality_score=0.95,
                    description="Recovered aluminum",
                )
            )

        # Calculate processing time
        processing_time = (total_input / self.max_capacity_kg_hr) + (self.residence_time_min / 60)

        # Calculate residue (mass not accounted for in products)
        product_total = sum(p.mass_kg for p in products)
        residue = max(0, total_input - product_total)

        return ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=products,
            waste_residue_kg=residue,
            mass_recovery_rate=product_total / total_input if total_input > 0 else 0,
            energy_consumed_kwh=self.get_energy_requirement(total_input),
            energy_recovered_kwh=energy_content / 3.6,  # MJ to kWh
            processing_time_hours=processing_time,
            toxins_released=toxins,
            microplastics_generated=microplastics,
        )


class MeltExtrusionProcess(RecyclingProcess):
    """
    Melt extrusion process for thermoplastic recycling.

    Shreds, melts, and extrudes plastics into filament or pellets.
    Operating temperature: 150-280°C depending on material.

    Suitable for: Thermoplastics (PE, PP, PET, etc.)
    Not suitable for: Thermosets, textiles, paper, metals
    """

    def __init__(
        self,
        max_capacity_kg_hr: float = 1.0,
        output_form: str = "filament",  # "filament" or "pellets"
    ):
        super().__init__("Melt Extrusion", max_capacity_kg_hr)
        self.output_form = output_form
        self.specific_energy_kwh_kg = 0.8  # Lower than pyrolysis

        # Only thermoplastics
        self.acceptable_materials = {"LDPE", "HDPE", "PP", "PET", "PE"}

    def can_process(self, waste_item: WasteItem) -> bool:
        # Check if primary material is a thermoplastic
        return waste_item.composition.primary_material in self.acceptable_materials

    def get_energy_requirement(self, mass_kg: float) -> float:
        return mass_kg * self.specific_energy_kwh_kg

    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """Process thermoplastics into filament or pellets."""
        total_input = sum(masses_kg)
        processable_mass = 0.0
        rejected_mass = 0.0

        for item, mass in zip(waste_items, masses_kg):
            if self.can_process(item):
                # Account for material losses during processing (~5-10%)
                processable_mass += mass * 0.92
            else:
                rejected_mass += mass

        # Output product
        product_type = (
            ProductType.FILAMENT if self.output_form == "filament" else ProductType.PELLETS
        )
        products = []

        if processable_mass > 0:
            products.append(
                Product(
                    product_type=product_type,
                    mass_kg=processable_mass,
                    quality_score=0.8,  # Recycled quality
                    description=f"Recycled plastic {self.output_form}",
                )
            )

        processing_time = total_input / self.max_capacity_kg_hr

        return ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=products,
            waste_residue_kg=rejected_mass + (total_input - processable_mass - rejected_mass),
            mass_recovery_rate=processable_mass / total_input if total_input > 0 else 0,
            energy_consumed_kwh=self.get_energy_requirement(processable_mass),
            processing_time_hours=processing_time,
            microplastics_generated=True,  # Concern during shredding
        )


class PlasmaProcess(RecyclingProcess):
    """
    Plasma arc gasification process.

    Ultra-high temperature (10,000-20,000°C) processing that
    vaporizes virtually any material into elemental components.

    Suitable for: All materials including difficult wastes
    Produces: Syngas, vitrified slag, recovered metals
    """

    def __init__(self, max_capacity_kg_hr: float = 0.5):
        super().__init__("Plasma Arc Gasification", max_capacity_kg_hr)
        self.specific_energy_kwh_kg = 5.0  # High energy requirement
        self.operating_temp_c = 15000.0

    def can_process(self, waste_item: WasteItem) -> bool:
        # Can process anything
        return True

    def get_energy_requirement(self, mass_kg: float) -> float:
        return mass_kg * self.specific_energy_kwh_kg

    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """Process waste through plasma gasification."""
        total_input = sum(masses_kg)

        # Plasma converts everything to syngas + vitrified slag
        syngas_mass = total_input * 0.75  # Most mass becomes gas
        slag_mass = total_input * 0.20  # Inert vitrified material
        metal_mass = total_input * 0.05  # Recovered metals

        # High energy recovery from complete gasification
        total_energy_mj = sum(
            mass * (item.heating_value_mj_kg or 20) for item, mass in zip(waste_items, masses_kg)
        )

        products = [
            Product(
                product_type=ProductType.SYNGAS,
                mass_kg=syngas_mass,
                quality_score=0.95,  # Very clean syngas
                energy_content_mj=total_energy_mj * 0.8,
                description="High-purity synthesis gas",
            ),
            Product(
                product_type=ProductType.ASH,
                mass_kg=slag_mass,
                quality_score=1.0,
                description="Vitrified slag (inert, can be used as construction material)",
            ),
            Product(
                product_type=ProductType.METAL,
                mass_kg=metal_mass,
                quality_score=0.9,
                description="Recovered metals",
            ),
        ]

        processing_time = total_input / self.max_capacity_kg_hr

        return ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=products,
            waste_residue_kg=0.0,  # Complete conversion
            mass_recovery_rate=1.0,
            energy_consumed_kwh=self.get_energy_requirement(total_input),
            energy_recovered_kwh=total_energy_mj * 0.8 / 3.6,
            processing_time_hours=processing_time,
            toxins_released=False,  # Destroyed at plasma temps
            microplastics_generated=False,
        )


class HeatMeltCompaction(RecyclingProcess):
    """
    Heat Melt Compaction (HMC) process.

    Based on NASA's Trash Compaction Processing System (TCPS).
    Uses heat and pressure to reduce volume and recover water.

    Suitable for: Mixed waste streams
    Produces: Compacted tiles, recovered water
    """

    def __init__(
        self,
        max_capacity_kg_hr: float = 2.0,
        operating_temp_c: float = 150.0,
        target_water_activity: float = 0.5,
    ):
        super().__init__("Heat Melt Compaction", max_capacity_kg_hr)
        self.operating_temp_c = operating_temp_c
        self.target_water_activity = target_water_activity
        self.specific_energy_kwh_kg = 0.5  # Relatively low energy

        # Volume reduction factor
        self.volume_reduction = 0.25  # Reduces to 25% of original volume

    def can_process(self, waste_item: WasteItem) -> bool:
        # Can process most waste types
        return True

    def get_energy_requirement(self, mass_kg: float) -> float:
        return mass_kg * self.specific_energy_kwh_kg

    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """Compact waste into tiles and recover water."""
        total_input = sum(masses_kg)

        # Calculate water recovery based on moisture content
        water_recovered = sum(
            mass * (item.moisture_content_percent / 100)
            for item, mass in zip(waste_items, masses_kg)
        )

        # Compacted tile mass (input minus water)
        tile_mass = total_input - water_recovered

        products = [
            Product(
                product_type=ProductType.COMPOSITE,
                mass_kg=tile_mass,
                quality_score=0.7,
                description="Compacted waste tile (can be used as radiation shielding)",
            ),
        ]

        if water_recovered > 0:
            products.append(
                Product(
                    product_type=ProductType.WATER,
                    mass_kg=water_recovered,
                    quality_score=0.5,  # Needs significant purification
                    description="Recovered water (requires treatment)",
                )
            )

        processing_time = total_input / self.max_capacity_kg_hr

        return ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=products,
            waste_residue_kg=0.0,
            mass_recovery_rate=(tile_mass + water_recovered) / total_input
            if total_input > 0
            else 0,
            energy_consumed_kwh=self.get_energy_requirement(total_input),
            processing_time_hours=processing_time,
        )


class CompositeManufacturing(RecyclingProcess):
    """
    Composite manufacturing process (inspired by CERBERUZ).

    Uses foam as reinforcing filler in thermoplastic matrix
    to create structural composite materials.

    Suitable for: Foam + thermoplastics combination
    Produces: Structural composites via injection molding/extrusion
    """

    def __init__(self, max_capacity_kg_hr: float = 0.5):
        super().__init__("Composite Manufacturing", max_capacity_kg_hr)
        self.specific_energy_kwh_kg = 1.2

    def can_process(self, waste_item: WasteItem) -> bool:
        # Processes foam and thermoplastics
        return (
            waste_item.category == WasteCategory.FOAM_PACKING
            or waste_item.composition.primary_material in {"LDPE", "HDPE", "PP", "PET", "PE"}
        )

    def get_energy_requirement(self, mass_kg: float) -> float:
        return mass_kg * self.specific_energy_kwh_kg

    def process(self, waste_items: list[WasteItem], masses_kg: list[float]) -> ProcessingResult:
        """Create composite materials from foam and plastics."""
        total_input = sum(masses_kg)

        foam_mass = 0.0
        plastic_mass = 0.0

        for item, mass in zip(waste_items, masses_kg):
            if item.category == WasteCategory.FOAM_PACKING:
                foam_mass += mass
            elif self.can_process(item):
                plastic_mass += mass

        # Optimal ratio is ~20-30% foam filler
        # Adjust based on available materials
        if foam_mass > 0 and plastic_mass > 0:
            total_processable = foam_mass + plastic_mass
            composite_mass = total_processable * 0.95  # 5% process loss
        elif plastic_mass > 0:
            composite_mass = plastic_mass * 0.92
        else:
            composite_mass = 0.0

        products = []
        if composite_mass > 0:
            products.append(
                Product(
                    product_type=ProductType.COMPOSITE,
                    mass_kg=composite_mass,
                    quality_score=0.85,
                    description="Thermoplastic-foam composite material",
                )
            )

        processing_time = total_input / self.max_capacity_kg_hr

        return ProcessingResult(
            input_mass_kg=total_input,
            input_waste_items=waste_items,
            products=products,
            waste_residue_kg=total_input - composite_mass,
            mass_recovery_rate=composite_mass / total_input if total_input > 0 else 0,
            energy_consumed_kwh=self.get_energy_requirement(total_input),
            processing_time_hours=processing_time,
        )
