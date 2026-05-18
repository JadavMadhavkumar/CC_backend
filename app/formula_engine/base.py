"""
Formula Engine - Core component for carbon credit calculations.
Dynamically loads and executes carbon calculation formulas.

Based on formulas defined in formula.md:
- General Carbon Credit Formula: CC = (E_baseline - E_project) × Q / 1000
- Plastic Waste Management formulas
- Agricultural Waste Management formulas
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Optional

import structlog

logger = structlog.get_logger(__name__)


class FormulaCategory(Enum):
    """Categories of carbon calculation formulas."""
    GENERAL = "general"
    PLASTIC_WASTE = "plastic_waste"
    AGRICULTURAL_WASTE = "agricultural_waste"
    BIOCHAR = "biochar"
    ENERGY = "energy"
    EMISSION = "emission"


class FormulaType(Enum):
    """Types of formulas based on disposal method."""
    # Plastic Waste
    PLASTIC_RECYCLING = "plastic_recycling"
    PET_RECYCLING = "pet_recycling"
    HDPE_RECYCLING = "hdpe_recycling"
    PVC_MANAGEMENT = "pvc_management"
    LDPE_RECYCLING = "ldpe_recycling"
    PP_WASTE = "pp_waste"
    PS_WASTE = "ps_waste"
    ABS_WASTE = "abs_waste"
    PC_WASTE = "pc_waste"
    NYLON_WASTE = "nylon_waste"
    PU_WASTE = "pu_waste"
    EPS_WASTE = "eps_waste"
    BIOPLASTIC_WASTE = "bioplastic_waste"
    MIXED_PLASTIC_PYROLYSIS = "mixed_plastic_pyrolysis"
    PLASTIC_WTE = "plastic_wte"  # Waste to Energy

    # Agricultural Waste
    AGRI_WASTE = "agri_waste"
    CROP_RESIDUE = "crop_residue"
    RICE_STRAW = "rice_straw"
    SUGARCANE_BAGASSE = "sugarcane_bagasse"
    CORN_STOVER = "corn_stover"
    WHEAT_STRAW = "wheat_straw"
    ANIMAL_MANURE = "animal_manure"
    COMPOSTING = "composting"
    BIOCHAR = "biochar"
    BIOGAS = "biogas"
    BIOMASS_POWER = "biomass_power"
    PALM_OIL_WASTE = "palm_oil_waste"
    COCONUT_SHELL = "coconut_shell"
    COFFEE_HUSK = "coffee_husk"
    TEA_WASTE = "tea_waste"
    FORESTRY_RESIDUE = "forestry_residue"


@dataclass
class CalculationInput:
    """Input parameters for carbon calculation."""
    quantity: float
    unit: str = "kg"
    waste_type: Optional[str] = None
    plastic_type: Optional[str] = None
    region: Optional[str] = None
    processing_method: Optional[str] = None
    disposal_method_baseline: Optional[str] = None
    disposal_method_project: Optional[str] = None
    feedstock_type: Optional[str] = None
    biochar_yield_percentage: Optional[float] = None
    carbon_content: Optional[float] = None
    energy_generated: Optional[float] = None
    gwp: float = 28.0  # Default CH4 GWP
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CalculationResult:
    """Result of carbon calculation."""
    formula_code: str
    formula_name: str
    formula_category: FormulaCategory
    baseline_emissions: float
    project_emissions: float
    emissions_reduced: float
    emissions_removed: float = 0.0
    carbon_credits_generated: float
    unit: str = "tCO2e"
    emission_factors_used: dict[str, float] = field(default_factory=dict)
    calculation_details: dict[str, Any] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    is_valid: bool = True
    validation_errors: list[str] = field(default_factory=list)


class FormulaBase(ABC):
    """Base class for all formula implementations."""

    def __init__(self):
        self.name: str = ""
        self.code: str = ""
        self.category: FormulaCategory = FormulaCategory.GENERAL
        self.description: str = ""
        self.formula_string: str = ""

    @abstractmethod
    def calculate(
        self,
        input_params: CalculationInput,
        emission_factors: dict[str, float]
    ) -> CalculationResult:
        """Execute the formula calculation."""
        pass

    def validate_input(
        self,
        input_params: CalculationInput
    ) -> list[str]:
        """Validate input parameters."""
        errors = []
        if input_params.quantity <= 0:
            errors.append("Quantity must be greater than 0")
        if not input_params.unit:
            errors.append("Unit is required")
        return errors


class GeneralCarbonCreditFormula(FormulaBase):
    """
    General Carbon Credit Formula:
    CC = (E_baseline - E_project) × Q / 1000

    Where:
    - CC = Carbon Credits generated (tCO2e)
    - E_baseline = Baseline emissions
    - E_project = Project emissions after mitigation
    - Q = Quantity of material processed
    """

    def __init__(self):
        super().__init__()
        self.name = "General Carbon Credit Formula"
        self.code = "CC_GENERAL"
        self.category = FormulaCategory.GENERAL
        self.description = "General formula for calculating carbon credits from emission reduction"
        self.formula_string = "CC = (E_baseline - E_project) × Q / 1000"

    def calculate(
        self,
        input_params: CalculationInput,
        emission_factors: dict[str, float]
    ) -> CalculationResult:
        """Execute general carbon credit calculation."""
        errors = self.validate_input(input_params)
        if errors:
            return CalculationResult(
                formula_code=self.code,
                formula_name=self.name,
                formula_category=self.category,
                baseline_emissions=0.0,
                project_emissions=0.0,
                emissions_reduced=0.0,
                carbon_credits_generated=0.0,
                is_valid=False,
                validation_errors=errors
            )

        ef_baseline = emission_factors.get("EF_baseline", 0.0)
        ef_project = emission_factors.get("EF_project", 0.0)

        baseline_emissions = ef_baseline * input_params.quantity
        project_emissions = ef_project * input_params.quantity
        emissions_reduced = baseline_emissions - project_emissions
        carbon_credits = emissions_reduced / 1000  # Convert kg to tCO2e

        return CalculationResult(
            formula_code=self.code,
            formula_name=self.name,
            formula_category=self.category,
            baseline_emissions=baseline_emissions,
            project_emissions=project_emissions,
            emissions_reduced=emissions_reduced,
            carbon_credits_generated=max(0, carbon_credits),
            emission_factors_used={
                "EF_baseline": ef_baseline,
                "EF_project": ef_project
            },
            calculation_details={
                "formula": self.formula_string,
                "quantity": input_params.quantity,
                "unit": input_params.unit
            }
        )


class PlasticWasteRecyclingFormula(FormulaBase):
    """
    Plastic Waste Recycling Formula:
    CC = (EF_landfill - EF_recycling) × W / 1000

    For specific plastic types:
    - PET: CC = (EF_PETlandfill - EF_PETrecycling) × W / 1000
    - HDPE: CC = (EF_HDPEdisposal - EF_HDPErecycling) × W / 1000
    - etc.
    """

    FORMULA_TEMPLATES = {
        FormulaType.PLASTIC_RECYCLING: "CC = (EF_landfill - EF_recycling) × W / 1000",
        FormulaType.PET_RECYCLING: "CC = (EF_PETlandfill - EF_PETrecycling) × W / 1000",
        FormulaType.HDPE_RECYCLING: "CC = (EF_HDPEdisposal - EF_HDPErecycling) × W / 1000",
        FormulaType.PVC_MANAGEMENT: "CC = (EF_PVCincineration - EF_PVCrecycling) × W / 1000",
        FormulaType.LDPE_RECYCLING: "CC = (EF_LDPElandfill - EF_LDPErecycling) × W / 1000",
        FormulaType.PP_WASTE: "CC = (EF_PPdisposal - EF_PPrecycling) × W / 1000",
        FormulaType.PS_WASTE: "CC = (EF_PSlandfill - EF_PSrecycling) × W / 1000",
        FormulaType.ABS_WASTE: "CC = (EF_ABSdisposal - EF_ABSrecycling) × W / 1000",
        FormulaType.PC_WASTE: "CC = (EF_PCdisposal - EF_PCrecycling) × W / 1000",
        FormulaType.NYLON_WASTE: "CC = (EF_nylondisposal - EF_nylonrecycling) × W / 1000",
        FormulaType.PU_WASTE: "CC = (EF_PUlandfill - EF_PUrecycling) × W / 1000",
        FormulaType.EPS_WASTE: "CC = (EF_EPSlandfill - EF_EPSrecycling) × W / 1000",
        FormulaType.BIOPLASTIC_WASTE: "CC = (EF_plasticlandfill - EF_composting) × W / 1000",
        FormulaType.MIXED_PLASTIC_PYROLYSIS: "CC = (EF_landfill - EF_pyrolysis) × W / 1000",
        FormulaType.PLASTIC_WTE: "CC = (EF_coalenergy - EF_plasticWTE) × E / 1000",
    }

    PLASTIC_TYPE_MAPPING = {
        "pet": FormulaType.PET_RECYCLING,
        "hdpe": FormulaType.HDPE_RECYCLING,
        "pvc": FormulaType.PVC_MANAGEMENT,
        "ldpe": FormulaType.LDPE_RECYCLING,
        "pp": FormulaType.PP_WASTE,
        "ps": FormulaType.PS_WASTE,
        "abs": FormulaType.ABS_WASTE,
        "pc": FormulaType.PC_WASTE,
        "nylon": FormulaType.NYLON_WASTE,
        "pu": FormulaType.PU_WASTE,
        "eps": FormulaType.EPS_WASTE,
        "bioplastic": FormulaType.BIOPLASTIC_WASTE,
        "mixed": FormulaType.MIXED_PLASTIC_PYROLYSIS,
    }

    def __init__(self):
        super().__init__()
        self.name = "Plastic Waste Recycling"
        self.code = "CC_PLASTIC_WASTE"
        self.category = FormulaCategory.PLASTIC_WASTE

    def calculate(
        self,
        input_params: CalculationInput,
        emission_factors: dict[str, float]
    ) -> CalculationResult:
        """Execute plastic waste carbon credit calculation."""
        errors = self.validate_input(input_params)
        if errors:
            return CalculationResult(
                formula_code=self.code,
                formula_name=self.name,
                formula_category=self.category,
                baseline_emissions=0.0,
                project_emissions=0.0,
                emissions_reduced=0.0,
                carbon_credits_generated=0.0,
                is_valid=False,
                validation_errors=errors
            )

        plastic_type = input_params.plastic_type.lower() if input_params.plastic_type else "plastic"
        formula_type = self.PLASTIC_TYPE_MAPPING.get(plastic_type, FormulaType.PLASTIC_RECYCLING)

        ef_baseline_key = f"EF_{plastic_type.upper()}_landfill"
        if formula_type == FormulaType.PLASTIC_WTE:
            ef_baseline_key = "EF_coalenergy"
        elif formula_type == FormulaType.MIXED_PLASTIC_PYROLYSIS:
            ef_baseline_key = "EF_landfill"

        ef_project_key = f"EF_{plastic_type.upper()}_recycling"
        if formula_type == FormulaType.PLASTIC_WTE:
            ef_project_key = "EF_plasticWTE"
        elif formula_type == FormulaType.BIOPLASTIC_WASTE:
            ef_project_key = "EF_composting"

        ef_baseline = emission_factors.get(ef_baseline_key, emission_factors.get("EF_landfill", 6.0))
        ef_project = emission_factors.get(ef_project_key, emission_factors.get("EF_recycling", 0.5))

        baseline_emissions = ef_baseline * input_params.quantity
        project_emissions = ef_project * input_params.quantity
        emissions_reduced = baseline_emissions - project_emissions
        carbon_credits = emissions_reduced / 1000

        return CalculationResult(
            formula_code=self.code,
            formula_name=f"Plastic Waste Recycling - {plastic_type.upper()}",
            formula_category=self.category,
            baseline_emissions=baseline_emissions,
            project_emissions=project_emissions,
            emissions_reduced=emissions_reduced,
            carbon_credits_generated=max(0, carbon_credits),
            emission_factors_used={
                ef_baseline_key: ef_baseline,
                ef_project_key: ef_project
            },
            calculation_details={
                "formula": self.FORMULA_TEMPLATES.get(formula_type, ""),
                "plastic_type": plastic_type,
                "quantity": input_params.quantity,
                "unit": input_params.unit
            }
        )


class AgriculturalWasteFormula(FormulaBase):
    """
    Agricultural Waste Management Formulas:
    - General: CC = (EF_openburning - EF_sustainablemanagement) × W / 1000
    - Crop Residue: CC = (EF_burning - EF_mulching) × W / 1000
    - Rice Straw: CC = (EF_strawburning - EF_biochar) × W / 1000
    - etc.
    """

    FORMULA_TEMPLATES = {
        FormulaType.AGRI_WASTE: "CC = (EF_openburning - EF_sustainablemanagement) × W / 1000",
        FormulaType.CROP_RESIDUE: "CC = (EF_burning - EF_mulching) × W / 1000",
        FormulaType.RICE_STRAW: "CC = (EF_strawburning - EF_biochar) × W / 1000",
        FormulaType.SUGARCANE_BAGASSE: "CC = (EF_coal - EF_bagasseenergy) × E / 1000",
        FormulaType.CORN_STOVER: "CC = (EF_burning - EF_composting) × W / 1000",
        FormulaType.WHEAT_STRAW: "CC = (EF_fieldburning - EF_biogas) × W / 1000",
        FormulaType.ANIMAL_MANURE: "CC = (CH4_baseline - CH4_biogas) × GWP / 1000",
        FormulaType.COMPOSTING: "CC = (EF_landfill - EF_compost) × W / 1000",
        FormulaType.BIOCHAR: "CC = (C_captured + EF_soilimprovement) × W / 1000",
        FormulaType.BIOGAS: "CC = (EF_fossilfuel - EF_biogasenergy) × E / 1000",
        FormulaType.BIOMASS_POWER: "CC = (EF_coalpower - EF_biomasspower) × E / 1000",
        FormulaType.PALM_OIL_WASTE: "CC = (CH4_POMEbaseline - CH4_capture) × GWP / 1000",
        FormulaType.COCONUT_SHELL: "CC = (EF_coal - EF_biomass) × E / 1000",
        FormulaType.COFFEE_HUSK: "CC = (EF_openburning - EF_biofuel) × W / 1000",
        FormulaType.TEA_WASTE: "CC = (EF_dumping - EF_composting) × W / 1000",
        FormulaType.FORESTRY_RESIDUE: "CC = (EF_decay - EF_bioenergy) × W / 1000",
    }

    WASTE_TYPE_MAPPING = {
        "agricultural": FormulaType.AGRI_WASTE,
        "crop_residue": FormulaType.CROP_RESIDUE,
        "rice_straw": FormulaType.RICE_STRAW,
        "sugarcane_bagasse": FormulaType.SUGARCANE_BAGASSE,
        "corn_stover": FormulaType.CORN_STOVER,
        "wheat_straw": FormulaType.WHEAT_STRAW,
        "animal_manure": FormulaType.ANIMAL_MANURE,
        "composting": FormulaType.COMPOSTING,
        "biogas": FormulaType.BIOGAS,
        "biomass_power": FormulaType.BIOMASS_POWER,
        "palm_oil_waste": FormulaType.PALM_OIL_WASTE,
        "coconut_shell": FormulaType.COCONUT_SHELL,
        "coffee_husk": FormulaType.COFFEE_HUSK,
        "tea_waste": FormulaType.TEA_WASTE,
        "forestry_residue": FormulaType.FORESTRY_RESIDUE,
    }

    def __init__(self):
        super().__init__()
        self.name = "Agricultural Waste Management"
        self.code = "CC_AGRI_WASTE"
        self.category = FormulaCategory.AGRICULTURAL_WASTE

    def calculate(
        self,
        input_params: CalculationInput,
        emission_factors: dict[str, float]
    ) -> CalculationResult:
        """Execute agricultural waste carbon credit calculation."""
        errors = self.validate_input(input_params)
        if errors:
            return CalculationResult(
                formula_code=self.code,
                formula_name=self.name,
                formula_category=self.category,
                baseline_emissions=0.0,
                project_emissions=0.0,
                emissions_reduced=0.0,
                carbon_credits_generated=0.0,
                is_valid=False,
                validation_errors=errors
            )

        waste_type = input_params.waste_type.lower() if input_params.waste_type else "agricultural"
        formula_type = self.WASTE_TYPE_MAPPING.get(waste_type, FormulaType.AGRI_WASTE)

        if formula_type in [FormulaType.SUGARCANE_BAGASSE, FormulaType.BIOGAS,
                            FormulaType.BIOMASS_POWER, FormulaType.COCONUT_SHELL]:
            energy = input_params.energy_generated or input_params.quantity
            ef_baseline = emission_factors.get("EF_coal", emission_factors.get("EF_openburning", 2.5))
            ef_project = emission_factors.get(f"EF_{waste_type}energy",
                                               emission_factors.get("EF_sustainablemanagement", 0.3))
            baseline_emissions = ef_baseline * energy
            project_emissions = ef_project * energy
        elif formula_type in [FormulaType.ANIMAL_MANURE, FormulaType.PALM_OIL_WASTE]:
            ch4_baseline = emission_factors.get("CH4_baseline", 10.0)
            ch4_project = emission_factors.get("CH4_biogas", emission_factors.get("CH4_capture", 1.0))
            gwp = input_params.gwp
            baseline_emissions = ch4_baseline * gwp * input_params.quantity / 1000
            project_emissions = ch4_project * gwp * input_params.quantity / 1000
        else:
            ef_baseline_key = "EF_openburning"
            ef_project_key = "EF_sustainablemanagement"

            if formula_type == FormulaType.CROP_RESIDUE:
                ef_baseline_key = "EF_burning"
                ef_project_key = "EF_mulching"
            elif formula_type == FormulaType.RICE_STRAW:
                ef_baseline_key = "EF_strawburning"
                ef_project_key = "EF_biochar"
            elif formula_type == FormulaType.COMPOSTING:
                ef_baseline_key = "EF_landfill"
                ef_project_key = "EF_compost"
            elif formula_type == FormulaType.COFFEE_HUSK:
                ef_baseline_key = "EF_openburning"
                ef_project_key = "EF_biofuel"
            elif formula_type == FormulaType.TEA_WASTE:
                ef_baseline_key = "EF_dumping"
                ef_project_key = "EF_composting"
            elif formula_type == FormulaType.FORESTRY_RESIDUE:
                ef_baseline_key = "EF_decay"
                ef_project_key = "EF_bioenergy"

            ef_baseline = emission_factors.get(ef_baseline_key, 3.0)
            ef_project = emission_factors.get(ef_project_key, 0.5)

            baseline_emissions = ef_baseline * input_params.quantity
            project_emissions = ef_project * input_params.quantity

        emissions_reduced = baseline_emissions - project_emissions
        carbon_credits = emissions_reduced / 1000

        return CalculationResult(
            formula_code=self.code,
            formula_name=f"Agricultural Waste - {waste_type}",
            formula_category=self.category,
            baseline_emissions=baseline_emissions,
            project_emissions=project_emissions,
            emissions_reduced=emissions_reduced,
            carbon_credits_generated=max(0, carbon_credits),
            calculation_details={
                "formula": self.FORMULA_TEMPLATES.get(formula_type, ""),
                "waste_type": waste_type,
                "quantity": input_params.quantity,
                "unit": input_params.unit
            }
        )


class BiocharFormula(FormulaBase):
    """
    Biochar Production Formula:
    CC = (C_captured + EF_soilimprovement) × W / 1000

    Where:
    - C_captured = Carbon captured in biochar (kg CO2e)
    - EF_soilimprovement = Soil improvement emission factor
    - W = Weight of biochar (kg)
    """

    def __init__(self):
        super().__init__()
        self.name = "Biochar Production"
        self.code = "CC_BIOCHAR"
        self.category = FormulaCategory.BIOCHAR
        self.description = "Calculate carbon credits from biochar production and soil application"
        self.formula_string = "CC = (C_captured + EF_soilimprovement) × W / 1000"

    def calculate(
        self,
        input_params: CalculationInput,
        emission_factors: dict[str, float]
    ) -> CalculationResult:
        """Execute biochar carbon credit calculation."""
        errors = self.validate_input(input_params)
        if errors:
            return CalculationResult(
                formula_code=self.code,
                formula_name=self.name,
                formula_category=self.category,
                baseline_emissions=0.0,
                project_emissions=0.0,
                emissions_reduced=0.0,
                carbon_credits_generated=0.0,
                is_valid=False,
                validation_errors=errors
            )

        biochar_yield = input_params.biochar_yield_percentage or 30.0
        carbon_content = input_params.carbon_content or 70.0

        biochar_quantity = input_params.quantity * (biochar_yield / 100)
        carbon_captured = biochar_quantity * (carbon_content / 100) * (44.0 / 12.0)

        soil_improvement_factor = emission_factors.get("EF_soilimprovement", 0.05)
        soil_carbon_enhancement = carbon_captured * soil_improvement_factor

        emissions_removed = carbon_captured + soil_carbon_enhancement
        carbon_credits = emissions_removed / 1000

        return CalculationResult(
            formula_code=self.code,
            formula_name=self.name,
            formula_category=self.category,
            baseline_emissions=0.0,
            project_emissions=0.0,
            emissions_reduced=soil_carbon_enhancement,
            emissions_removed=emissions_removed,
            carbon_credits_generated=max(0, carbon_credits),
            emission_factors_used={
                "EF_soilimprovement": soil_improvement_factor
            },
            calculation_details={
                "formula": self.formula_string,
                "biochar_yield_percentage": biochar_yield,
                "carbon_content_percentage": carbon_content,
                "biochar_quantity": biochar_quantity,
                "carbon_captured_kg": carbon_captured,
                "soil_carbon_enhancement": soil_carbon_enhancement
            }
        )


class FormulaEngine:
    """
    Formula Engine - Main orchestration class for carbon credit calculations.
    Supports dynamic formula loading, validation, and execution.
    """

    def __init__(self):
        self._formulas: dict[str, FormulaBase] = {}
        self._emission_factors: dict[str, dict[str, float]] = {}
        self._register_default_formulas()
        self._load_default_emission_factors()
        logger.info("Formula engine initialized with default formulas and factors")

    def _register_default_formulas(self) -> None:
        """Register all default formula implementations."""
        self._formulas["CC_GENERAL"] = GeneralCarbonCreditFormula()
        self._formulas["CC_PLASTIC_WASTE"] = PlasticWasteRecyclingFormula()
        self._formulas["CC_AGRI_WASTE"] = AgriculturalWasteFormula()
        self._formulas["CC_BIOCHAR"] = BiocharFormula()

    def _load_default_emission_factors(self) -> None:
        """Load default emission factors from formula.md constants."""
        self._emission_factors["default"] = {
            # Plastic Waste (kg CO2e per kg of plastic)
            "EF_landfill": 6.0,
            "EF_recycling": 0.5,
            "EF_PET_landfill": 6.4,
            "EF_PET_recycling": 0.8,
            "EF_HDPE_landfill": 7.2,
            "EF_HDPE_recycling": 0.6,
            "EF_PVC_landfill": 8.1,
            "EF_PVC_recycling": 0.7,
            "EF_LDPE_landfill": 6.8,
            "EF_LDPE_recycling": 0.5,
            "EF_PP_landfill": 6.6,
            "EF_PP_recycling": 0.5,
            "EF_PS_landfill": 7.0,
            "EF_PS_recycling": 0.6,
            "EF_ABS_landfill": 9.0,
            "EF_ABS_recycling": 0.8,
            "EF_PC_landfill": 10.5,
            "EF_PC_recycling": 1.0,
            "EF_NYLON_landfill": 11.2,
            "EF_NYLON_recycling": 1.2,
            "EF_PU_landfill": 12.5,
            "EF_PU_recycling": 1.5,
            "EF_EPS_landfill": 3.2,
            "EF_EPS_recycling": 0.3,
            "EF_composting": 0.2,
            "EF_pyrolysis": 1.5,
            "EF_plasticWTE": 1.8,
            "EF_coalenergy": 2.5,
            # Agricultural Waste (kg CO2e per kg)
            "EF_openburning": 3.0,
            "EF_sustainablemanagement": 0.3,
            "EF_burning": 2.8,
            "EF_mulching": 0.2,
            "EF_strawburning": 2.5,
            "EF_biochar": 0.1,
            "EF_coal": 2.5,
            "EF_bagasseenergy": 0.4,
            "EF_compost": 0.15,
            "EF_biogas": 0.15,
            "EF_fossilfuel": 2.3,
            "EF_biogasenergy": 0.3,
            "EF_coalpower": 0.9,
            "EF_biomasspower": 0.15,
            "EF_decay": 1.5,
            "EF_bioenergy": 0.2,
            "EF_dumping": 2.0,
            "EF_biofuel": 0.4,
            # Biochar
            "EF_soilimprovement": 0.05,
            # GWP
            "GWP_CH4": 28.0,
            "GWP_N2O": 265.0,
            "CH4_baseline": 10.0,
            "CH4_biogas": 1.0,
            "CH4_capture": 0.5,
            "CH4_POMEbaseline": 25.0,
        }

    def register_formula(self, formula: FormulaBase) -> None:
        """Register a custom formula."""
        self._formulas[formula.code] = formula
        logger.info(f"Registered formula: {formula.code}")

    def register_emission_factors(
        self,
        region: str,
        factors: dict[str, float]
    ) -> None:
        """Register emission factors for a specific region."""
        self._emission_factors[region] = factors
        logger.info(f"Registered emission factors for region: {region}")

    def get_formula(self, code: str) -> Optional[FormulaBase]:
        """Get a formula by code."""
        return self._formulas.get(code)

    def get_emission_factors(
        self,
        region: Optional[str] = None
    ) -> dict[str, float]:
        """Get emission factors for a region."""
        if region and region in self._emission_factors:
            default_factors = self._emission_factors.get("default", {})
            region_factors = self._emission_factors.get(region, {})
            return {**default_factors, **region_factors}
        return self._emission_factors.get("default", {})

    def calculate(
        self,
        formula_code: str,
        input_params: CalculationInput,
        region: Optional[str] = None
    ) -> CalculationResult:
        """Execute a calculation using a specific formula."""
        formula = self.get_formula(formula_code)
        if not formula:
            logger.error(f"Formula not found: {formula_code}")
            return CalculationResult(
                formula_code=formula_code,
                formula_name="Unknown",
                formula_category=FormulaCategory.GENERAL,
                baseline_emissions=0.0,
                project_emissions=0.0,
                emissions_reduced=0.0,
                carbon_credits_generated=0.0,
                is_valid=False,
                validation_errors=[f"Formula not found: {formula_code}"]
            )

        emission_factors = self.get_emission_factors(region)
        result = formula.calculate(input_params, emission_factors)

        logger.info(
            f"Calculation completed: {formula_code}",
            carbon_credits=result.carbon_credits_generated,
            emissions_reduced=result.emissions_reduced,
            is_valid=result.is_valid
        )

        return result

    def calculate_waste_credit(
        self,
        waste_type: str,
        plastic_type: Optional[str],
        quantity: float,
        unit: str,
        processing_method: str,
        region: Optional[str] = None
    ) -> CalculationResult:
        """Calculate carbon credits for waste processing."""
        formula_code = "CC_PLASTIC_WASTE"
        if waste_type in ["agricultural", "crop_residue", "rice_straw", "composting"]:
            formula_code = "CC_AGRI_WASTE"

        input_params = CalculationInput(
            quantity=quantity,
            unit=unit,
            waste_type=waste_type,
            plastic_type=plastic_type,
            processing_method=processing_method
        )

        return self.calculate(formula_code, input_params, region)

    def calculate_biochar_credit(
        self,
        feedstock_quantity: float,
        biochar_yield: float,
        carbon_content: float,
        region: Optional[str] = None
    ) -> CalculationResult:
        """Calculate carbon credits for biochar production."""
        input_params = CalculationInput(
            quantity=feedstock_quantity,
            biochar_yield_percentage=biochar_yield,
            carbon_content=carbon_content
        )

        return self.calculate("CC_BIOCHAR", input_params, region)

    def get_available_formulas(self) -> list[dict[str, Any]]:
        """Get list of all available formulas."""
        return [
            {
                "code": code,
                "name": formula.name,
                "category": formula.category.value,
                "description": formula.description,
                "formula_string": formula.formula_string
            }
            for code, formula in self._formulas.items()
        ]


formula_engine = FormulaEngine()