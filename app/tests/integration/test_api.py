"""
Integration tests for API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check returns healthy status."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns API info."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestAuthenticationAPI:
    """Tests for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient, sample_user_data: dict):
        """Test user registration."""
        response = await client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, sample_user_data: dict):
        """Test registration with duplicate email fails."""
        await client.post("/api/v1/auth/register", json=sample_user_data)

        response = await client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == 400


class TestWasteAPI:
    """Tests for waste management endpoints."""

    @pytest.mark.asyncio
    async def test_get_waste_records_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting waste records returns empty list."""
        response = await client.get("/api/v1/waste/", headers=auth_headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_calculate_waste_credits(self, client: AsyncClient, auth_headers: dict):
        """Test waste credit calculation endpoint."""
        calc_data = {
            "waste_type": "plastic",
            "plastic_type": "PET",
            "quantity": 1000,
            "unit": "kg",
            "processing_method": "recycling",
            "disposal_method_baseline": "landfill",
            "disposal_method_project": "recycling",
        }

        response = await client.post(
            "/api/v1/waste/calculate", json=calc_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "carbon_credits_generated" in data
        assert data["carbon_credits_generated"] > 0


class TestBiocharAPI:
    """Tests for biochar endpoints."""

    @pytest.mark.asyncio
    async def test_get_biochar_records_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting biochar records returns empty list."""
        response = await client.get("/api/v1/biochar/", headers=auth_headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_calculate_biochar_credits(self, client: AsyncClient, auth_headers: dict):
        """Test biochar credit calculation endpoint."""
        calc_data = {
            "feedstock_type": "wood",
            "feedstock_quantity": 1000,
            "feedstock_unit": "kg",
            "biochar_yield_percentage": 30.0,
            "carbon_content": 70.0,
            "apply_soil_improvement": True,
        }

        response = await client.post(
            "/api/v1/biochar/calculate", json=calc_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_carbon_credits" in data
        assert data["total_carbon_credits"] > 0


class TestCarbonCreditAPI:
    """Tests for carbon credit endpoints."""

    @pytest.mark.asyncio
    async def test_get_carbon_credits_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting carbon credits returns empty list."""
        response = await client.get("/api/v1/carbon-credits/", headers=auth_headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_carbon_credits_stats(self, client: AsyncClient, auth_headers: dict):
        """Test getting carbon credit statistics."""
        response = await client.get("/api/v1/carbon-credits/stats/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_credits" in data
        assert "pending_credits" in data
