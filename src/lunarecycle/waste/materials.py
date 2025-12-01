"""
Material property database for waste recycling simulation.

Contains thermodynamic, physical, and chemical properties of materials
commonly found in space mission waste streams.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class MaterialType(Enum):
    """Classification of material types."""
    THERMOPLASTIC = auto()
    THERMOSET = auto()
    NATURAL_FIBER = auto()
    SYNTHETIC_FIBER = auto()
    METAL = auto()
    CELLULOSE = auto()
    COMPOSITE = auto()
    FOAM = auto()


@dataclass
class ThermalProperties:
    """Thermal properties of a material."""
    melting_point_c: Optional[float] = None  # None for non-melting materials
    glass_transition_c: Optional[float] = None
    decomposition_temp_c: float = 500.0
    specific_heat_j_kg_k: float = 1000.0  # J/(kg·K)
    thermal_conductivity_w_m_k: float = 0.2  # W/(m·K)
    heat_of_fusion_kj_kg: Optional[float] = None


@dataclass
class ChemicalProperties:
    """Chemical properties relevant to recycling."""
    formula: str
    molecular_weight: Optional[float] = None
    carbon_content_percent: float = 0.0
    hydrogen_content_percent: float = 0.0
    oxygen_content_percent: float = 0.0
    nitrogen_content_percent: float = 0.0
    other_elements: dict[str, float] = None

    def __post_init__(self):
        if self.other_elements is None:
            self.other_elements = {}


@dataclass
class PyrolysisProducts:
    """Expected products from pyrolysis of this material."""
    syngas_yield_percent: float = 0.0  # CO, H2, CH4
    oil_yield_percent: float = 0.0
    char_yield_percent: float = 0.0
    water_yield_percent: float = 0.0

    def __post_init__(self):
        total = (self.syngas_yield_percent + self.oil_yield_percent +
                 self.char_yield_percent + self.water_yield_percent)
        if total > 101.0:  # Allow small rounding
            raise ValueError(f"Pyrolysis products cannot exceed 100%, got {total}%")


@dataclass
class MaterialProperty:
    """Complete material property specification."""
    name: str
    material_type: MaterialType
    density_kg_m3: float
    heating_value_mj_kg: float  # Lower heating value (LHV)

    thermal: ThermalProperties
    chemical: ChemicalProperties
    pyrolysis: PyrolysisProducts

    # Recycling characteristics
    recyclability_score: float = 0.5  # 0-1 scale
    requires_sorting: bool = False
    contamination_sensitivity: float = 0.5  # 0-1 (1 = very sensitive)

    # Environmental concerns
    releases_toxins: bool = False
    creates_microplastics: bool = False
    pfas_containing: bool = False


class Material:
    """
    Database of material properties for waste stream components.

    Data based on literature values and NASA research on space waste processing.
    """

    # === POLYETHYLENE (LDPE/HDPE) ===
    LDPE = MaterialProperty(
        name="Low-Density Polyethylene",
        material_type=MaterialType.THERMOPLASTIC,
        density_kg_m3=920.0,
        heating_value_mj_kg=46.0,
        thermal=ThermalProperties(
            melting_point_c=115.0,
            glass_transition_c=-110.0,
            decomposition_temp_c=350.0,
            specific_heat_j_kg_k=2300.0,
            thermal_conductivity_w_m_k=0.33,
            heat_of_fusion_kj_kg=100.0
        ),
        chemical=ChemicalProperties(
            formula="(C2H4)n",
            carbon_content_percent=85.7,
            hydrogen_content_percent=14.3,
        ),
        pyrolysis=PyrolysisProducts(
            syngas_yield_percent=15.0,
            oil_yield_percent=80.0,
            char_yield_percent=5.0,
        ),
        recyclability_score=0.9,
        creates_microplastics=True
    )

    HDPE = MaterialProperty(
        name="High-Density Polyethylene",
        material_type=MaterialType.THERMOPLASTIC,
        density_kg_m3=960.0,
        heating_value_mj_kg=46.0,
        thermal=ThermalProperties(
            melting_point_c=130.0,
            glass_transition_c=-110.0,
            decomposition_temp_c=380.0,
            specific_heat_j_kg_k=1900.0,
            thermal_conductivity_w_m_k=0.48,
            heat_of_fusion_kj_kg=180.0
        ),
        chemical=ChemicalProperties(
            formula="(C2H4)n",
            carbon_content_percent=85.7,
            hydrogen_content_percent=14.3,
        ),
        pyrolysis=PyrolysisProducts(
            syngas_yield_percent=12.0,
            oil_yield_percent=82.0,
            char_yield_percent=6.0,
        ),
        recyclability_score=0.9,
        creates_microplastics=True
    )

    # === POLYPROPYLENE ===
    PP = MaterialProperty(
        name="Polypropylene",
        material_type=MaterialType.THERMOPLASTIC,
        density_kg_m3=905.0,
        heating_value_mj_kg=44.0,
        thermal=ThermalProperties(
            melting_point_c=160.0,
            glass_transition_c=-10.0,
            decomposition_temp_c=380.0,
            specific_heat_j_kg_k=1920.0,
            thermal_conductivity_w_m_k=0.22,
            heat_of_fusion_kj_kg=100.0
        ),
        chemical=ChemicalProperties(
            formula="(C3H6)n",
            carbon_content_percent=85.7,
            hydrogen_content_percent=14.3,
        ),
        pyrolysis=PyrolysisProducts(
            syngas_yield_percent=10.0,
            oil_yield_percent=85.0,
            char_yield_percent=5.0,
        ),
        recyclability_score=0.85,
        creates_microplastics=True
    )

    # === PET (Polyethylene Terephthalate) ===
    PET = MaterialProperty(
        name="Polyethylene Terephthalate",
        material_type=MaterialType.THERMOPLASTIC,
        density_kg_m3=1380.0,
        heating_value_mj_kg=23.0,
        thermal=ThermalProperties(
            melting_point_c=260.0,
            glass_transition_c=70.0,
            decomposition_temp_c=400.0,
            specific_heat_j_kg_k=1200.0,
            thermal_conductivity_w_m_k=0.24,
            heat_of_fusion_kj_kg=140.0
        ),
        chemical=ChemicalProperties(
            formula="(C10H8O4)n",
            carbon_content_percent=62.5,
            hydrogen_content_percent=4.2,
            oxygen_content_percent=33.3,
        ),
        pyrolysis=PyrolysisProducts(
            syngas_yield_percent=25.0,
            oil_yield_percent=55.0,
            char_yield_percent=15.0,
            water_yield_percent=5.0
        ),
        recyclability_score=0.8,
        creates_microplastics=True
    )

    # === PVDF (Zotek foam material) ===
    PVDF = MaterialProperty(
        name="Polyvinylidene Fluoride",
        material_type=MaterialType.FOAM,
        density_kg_m3=1780.0,  # Solid density; foam is ~25-30 kg/m³
        heating_value_mj_kg=13.0,
        thermal=ThermalProperties(
            melting_point_c=170.0,
            glass_transition_c=-40.0,
            decomposition_temp_c=450.0,
            specific_heat_j_kg_k=1300.0,
            thermal_conductivity_w_m_k=0.19,
            heat_of_fusion_kj_kg=50.0
        ),
        chemical=ChemicalProperties(
            formula="(C2H2F2)n",
            carbon_content_percent=37.5,
            hydrogen_content_percent=3.1,
            other_elements={"F": 59.4}
        ),
        pyrolysis=PyrolysisProducts(
            syngas_yield_percent=30.0,  # HF release concern!
            oil_yield_percent=20.0,
            char_yield_percent=40.0,
            water_yield_percent=10.0
        ),
        recyclability_score=0.3,  # Difficult due to fluorine
        releases_toxins=True,  # HF gas at high temperatures
        pfas_containing=True
    )

    # === POLYESTER ===
    POLYESTER = MaterialProperty(
        name="Polyester (PET fiber)",
        material_type=MaterialType.SYNTHETIC_FIBER,
        density_kg_m3=1380.0,
        heating_value_mj_kg=23.0,
        thermal=ThermalProperties(
            melting_point_c=260.0,
            glass_transition_c=70.0,
            decomposition_temp_c=400.0,
            specific_heat_j_kg_k=1200.0,
            thermal_conductivity_w_m_k=0.15,
            heat_of_fusion_kj_kg=140.0
        ),
        chemical=ChemicalProperties(
            formula="(C10H8O4)n",
            carbon_content_percent=62.5,
            hydrogen_content_percent=4.2,
            oxygen_content_percent=33.3,
        ),
        pyrolysis=PyrolysisProducts(
            syngas_yield_percent=25.0,
            oil_yield_percent=50.0,
            char_yield_percent=20.0,
            water_yield_percent=5.0
        ),
        recyclability_score=0.7,
        creates_microplastics=True
    )

    # === NYLON ===
    NYLON = MaterialProperty(
        name="Nylon 6/6",
        material_type=MaterialType.SYNTHETIC_FIBER,
        density_kg_m3=1140.0,
        heating_value_mj_kg=31.0,
        thermal=ThermalProperties(
            melting_point_c=265.0,
            glass_transition_c=50.0,
            decomposition_temp_c=420.0,
            specific_heat_j_kg_k=1700.0,
            thermal_conductivity_w_m_k=0.25,
            heat_of_fusion_kj_kg=95.0
        ),
        chemical=ChemicalProperties(
            formula="(C12H22N2O2)n",
            carbon_content_percent=63.7,
            hydrogen_content_percent=9.8,
            oxygen_content_percent=14.2,
            nitrogen_content_percent=12.4,
        ),
        pyrolysis=PyrolysisProducts(
            syngas_yield_percent=20.0,
            oil_yield_percent=55.0,
            char_yield_percent=15.0,
            water_yield_percent=10.0
        ),
        recyclability_score=0.6,
        creates_microplastics=True
    )

    # === COTTON ===
    COTTON = MaterialProperty(
        name="Cotton (Cellulose)",
        material_type=MaterialType.NATURAL_FIBER,
        density_kg_m3=1550.0,
        heating_value_mj_kg=17.0,
        thermal=ThermalProperties(
            decomposition_temp_c=350.0,
            specific_heat_j_kg_k=1300.0,
            thermal_conductivity_w_m_k=0.04,
        ),
        chemical=ChemicalProperties(
            formula="(C6H10O5)n",
            carbon_content_percent=44.4,
            hydrogen_content_percent=6.2,
            oxygen_content_percent=49.4,
        ),
        pyrolysis=PyrolysisProducts(
            syngas_yield_percent=35.0,
            oil_yield_percent=25.0,
            char_yield_percent=25.0,
            water_yield_percent=15.0
        ),
        recyclability_score=0.7,
    )

    # === ALUMINUM (for multi-layer packaging) ===
    ALUMINUM = MaterialProperty(
        name="Aluminum",
        material_type=MaterialType.METAL,
        density_kg_m3=2700.0,
        heating_value_mj_kg=0.0,  # Does not combust
        thermal=ThermalProperties(
            melting_point_c=660.0,
            specific_heat_j_kg_k=900.0,
            thermal_conductivity_w_m_k=237.0,
            heat_of_fusion_kj_kg=400.0
        ),
        chemical=ChemicalProperties(
            formula="Al",
            molecular_weight=27.0,
        ),
        pyrolysis=PyrolysisProducts(
            char_yield_percent=100.0,  # Remains as metal
        ),
        recyclability_score=0.95,
        requires_sorting=True
    )

    # === CELLULOSE (Paper) ===
    CELLULOSE = MaterialProperty(
        name="Cellulose (Paper)",
        material_type=MaterialType.CELLULOSE,
        density_kg_m3=700.0,  # Paper density
        heating_value_mj_kg=17.0,
        thermal=ThermalProperties(
            decomposition_temp_c=250.0,
            specific_heat_j_kg_k=1400.0,
            thermal_conductivity_w_m_k=0.05,
        ),
        chemical=ChemicalProperties(
            formula="(C6H10O5)n",
            carbon_content_percent=44.4,
            hydrogen_content_percent=6.2,
            oxygen_content_percent=49.4,
        ),
        pyrolysis=PyrolysisProducts(
            syngas_yield_percent=30.0,
            oil_yield_percent=30.0,
            char_yield_percent=20.0,
            water_yield_percent=20.0
        ),
        recyclability_score=0.8,
    )

    # === ACTIVATED CARBON ===
    ACTIVATED_CARBON = MaterialProperty(
        name="Activated Carbon",
        material_type=MaterialType.COMPOSITE,
        density_kg_m3=500.0,
        heating_value_mj_kg=32.0,
        thermal=ThermalProperties(
            decomposition_temp_c=700.0,  # Very stable
            specific_heat_j_kg_k=710.0,
            thermal_conductivity_w_m_k=0.15,
        ),
        chemical=ChemicalProperties(
            formula="C",
            carbon_content_percent=95.0,
            oxygen_content_percent=5.0,
        ),
        pyrolysis=PyrolysisProducts(
            char_yield_percent=90.0,
            syngas_yield_percent=10.0,
        ),
        recyclability_score=0.5,  # Can be regenerated
    )

    @classmethod
    def get_all(cls) -> list[MaterialProperty]:
        """Get all defined materials."""
        return [
            cls.LDPE, cls.HDPE, cls.PP, cls.PET, cls.PVDF,
            cls.POLYESTER, cls.NYLON, cls.COTTON, cls.ALUMINUM,
            cls.CELLULOSE, cls.ACTIVATED_CARBON
        ]

    @classmethod
    def get_by_name(cls, name: str) -> Optional[MaterialProperty]:
        """Find material by name (case-insensitive)."""
        name_lower = name.lower()
        for mat in cls.get_all():
            if mat.name.lower() == name_lower or name_lower in mat.name.lower():
                return mat
        return None

    @classmethod
    def get_thermoplastics(cls) -> list[MaterialProperty]:
        """Get all thermoplastic materials."""
        return [m for m in cls.get_all() if m.material_type == MaterialType.THERMOPLASTIC]
