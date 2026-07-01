"""
Unit tests for Formula Engine.
"""

from app.formula_engine.base import (
    FormulaEngine,
    CalculationInput,
    GeneralCarbonCreditFormula,
    PlasticWasteRecyclingFormula,
    AgriculturalWasteFormula,
    BiocharFormula,
    FormulaCategory,
)


class TestGeneralCarbonCreditFormula:
    """Tests for General Carbon Credit Formula."""

    def test_calculate_basic(self):
        """Test basic carbon credit calculation."""
        formula = GeneralCarbonCreditFormula()
        input_params = CalculationInput(
            quantity=1000,
            unit="kg",
            disposal_method_baseline="landfill",
            disposal_method_project="recycling",
        )
        emission_factors = {"EF_baseline": 6.0, "EF_project": 0.5}

        result = formula.calculate(input_params, emission_factors)

        assert result.is_valid is True
        assert result.baseline_emissions == 6000.0
        assert result.project_emissions == 500.0
        assert result.emissions_reduced == 5500.0
        assert result.carbon_credits_generated == 5.5

    def test_validate_input_invalid(self):
        """Test input validation with invalid data."""
        formula = GeneralCarbonCreditFormula()
        input_params = CalculationInput(quantity=0, unit="kg")

        errors = formula.validate_input(input_params)
        assert len(errors) > 0


class TestPlasticWasteRecyclingFormula:
    """Tests for Plastic Waste Recycling Formula."""

    def test_calculate_pet_recycling(self):
        """Test PET plastic recycling carbon credit calculation."""
        formula = PlasticWasteRecyclingFormula()
        input_params = CalculationInput(
            quantity=1000, unit="kg", plastic_type="pet", processing_method="recycling"
        )
        emission_factors = {"EF_PET_landfill": 6.4, "EF_PET_recycling": 0.8}

        result = formula.calculate(input_params, emission_factors)

        assert result.is_valid is True
        assert result.formula_category == FormulaCategory.PLASTIC_WASTE
        assert result.carbon_credits_generated > 0

    def test_calculate_hdpe_recycling(self):
        """Test HDPE plastic recycling carbon credit calculation."""
        formula = PlasticWasteRecyclingFormula()
        input_params = CalculationInput(quantity=500, unit="kg", plastic_type="hdpe")
        emission_factors = {"EF_HDPE_landfill": 7.2, "EF_HDPE_recycling": 0.6}

        result = formula.calculate(input_params, emission_factors)

        assert result.is_valid is True
        assert result.carbon_credits_generated > 0


class TestAgriculturalWasteFormula:
    """Tests for Agricultural Waste Formula."""

    def test_calculate_crop_residue(self):
        """Test crop residue management carbon credit calculation."""
        formula = AgriculturalWasteFormula()
        input_params = CalculationInput(quantity=1000, unit="kg", waste_type="crop_residue")
        emission_factors = {"EF_burning": 2.8, "EF_mulching": 0.2}

        result = formula.calculate(input_params, emission_factors)

        assert result.is_valid is True
        assert result.formula_category == FormulaCategory.AGRICULTURAL_WASTE

    def test_calculate_rice_straw(self):
        """Test rice straw biochar carbon credit calculation."""
        formula = AgriculturalWasteFormula()
        input_params = CalculationInput(quantity=1000, unit="kg", waste_type="rice_straw")
        emission_factors = {"EF_strawburning": 2.5, "EF_biochar": 0.1}

        result = formula.calculate(input_params, emission_factors)

        assert result.is_valid is True


class TestBiocharFormula:
    """Tests for Biochar Formula."""

    def test_calculate_biochar_credits(self):
        """Test biochar carbon credit calculation."""
        formula = BiocharFormula()
        input_params = CalculationInput(
            quantity=1000, biochar_yield_percentage=30.0, carbon_content=70.0
        )
        emission_factors = {"EF_soilimprovement": 0.05}

        result = formula.calculate(input_params, emission_factors)

        assert result.is_valid is True
        assert result.formula_category == FormulaCategory.BIOCHAR
        assert result.emissions_removed > 0
        assert result.carbon_credits_generated > 0

    def test_biochar_carbon_captured(self):
        """Test biochar carbon captured calculation."""
        formula = BiocharFormula()
        input_params = CalculationInput(
            quantity=1000, biochar_yield_percentage=30.0, carbon_content=70.0
        )
        emission_factors = {"EF_soilimprovement": 0.05}

        result = formula.calculate(input_params, emission_factors)

        biochar_quantity = 1000 * (30.0 / 100)
        expected_carbon = biochar_quantity * (70.0 / 100) * (44.0 / 12.0)

        assert result.calculation_details["biochar_quantity"] == biochar_quantity
        assert abs(result.calculation_details["carbon_captured_kg"] - expected_carbon) < 0.1


class TestFormulaEngine:
    """Tests for Formula Engine."""

    def test_engine_initialization(self):
        """Test formula engine initialization."""
        engine = FormulaEngine()

        assert len(engine.get_available_formulas()) > 0

        default_factors = engine.get_emission_factors()
        assert "EF_landfill" in default_factors
        assert "EF_recycling" in default_factors

    def test_calculate_waste_credit(self):
        """Test waste credit calculation via engine."""
        engine = FormulaEngine()

        result = engine.calculate_waste_credit(
            waste_type="plastic",
            plastic_type="pet",
            quantity=1000,
            unit="kg",
            processing_method="recycling",
        )

        assert result.is_valid is True
        assert result.carbon_credits_generated > 0

    def test_calculate_biochar_credit(self):
        """Test biochar credit calculation via engine."""
        engine = FormulaEngine()

        result = engine.calculate_biochar_credit(
            feedstock_quantity=1000, biochar_yield=30.0, carbon_content=70.0
        )

        assert result.is_valid is True
        assert result.carbon_credits_generated > 0

    def test_register_custom_emission_factors(self):
        """Test registering custom emission factors for a region."""
        engine = FormulaEngine()

        custom_factors = {"EF_landfill": 5.0, "EF_recycling": 0.3}

        engine.register_emission_factors("custom_region", custom_factors)

        region_factors = engine.get_emission_factors("custom_region")
        assert region_factors["EF_landfill"] == 5.0
        assert region_factors["EF_recycling"] == 0.3

    def test_get_formula(self):
        """Test getting a formula by code."""
        engine = FormulaEngine()

        formula = engine.get_formula("CC_GENERAL")
        assert formula is not None
        assert formula.code == "CC_GENERAL"

        formula = engine.get_formula("NONEXISTENT")
        assert formula is None
