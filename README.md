# Carbon Credit Platform Backend

Production-grade Carbon Credit Management Platform built with Python FastAPI.

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [API Endpoints](#api-endpoints)
5. [Authentication](#authentication)
6. [Carbon Calculation Engine](#carbon-calculation-engine)
7. [Database Models](#database-models)
8. [Services](#services)
9. [Configuration](#configuration)
10. [Docker & Deployment](#docker--deployment)
11. [CI/CD Pipeline](#cicd-pipeline)
12. [Getting Started](#getting-started)

---

## Overview

The Carbon Credit Platform Backend provides:
- Carbon credit calculation from plastic waste, agricultural waste, and biochar
- JWT-based authentication with Role-Based Access Control (RBAC)
- PostgreSQL database with async SQLAlchemy 2.0
- RESTful API with FastAPI
- Docker and Kubernetes deployment support
- GitHub Actions CI/CD pipeline

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Language | Python 3.12+ |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Authentication | JWT with refresh tokens |
| Caching | Redis |
| Task Queue | Celery |
| Testing | Pytest |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |

---

## Project Structure

```
CC_backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/          # API route handlers
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── organization.py  # Organization CRUD
│   │   │   ├── waste.py        # Waste management
│   │   │   ├── biochar.py      # Biochar tracking
│   │   │   └── carbon_credit.py # Carbon credit management
│   │   └── router.py           # Main API router
│   ├── core/
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database connection
│   │   ├── security.py         # JWT & password handling
│   │   └── logging.py          # Logging configuration
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── waste.py
│   │   ├── biochar.py
│   │   ├── carbon_credit.py
│   │   ├── emission.py
│   │   ├── verification.py
│   │   └── ...
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── waste.py
│   │   ├── biochar.py
│   │   └── carbon_credit.py
│   ├── services/               # Business logic layer
│   │   ├── auth.py
│   │   ├── waste.py
│   │   ├── biochar.py
│   │   ├── carbon_credit.py
│   │   └── verification.py
│   ├── formula_engine/          # Carbon calculation engine
│   │   └── base.py
│   ├── middleware/             # Custom middleware
│   │   ├── rate_limit.py
│   │   └── security.py
│   ├── workers/                # Celery background tasks
│   ├── tests/                  # Unit & integration tests
│   └── main.py                 # FastAPI app entry point
├── .github/workflows/          # CI/CD pipeline
├── Dockerfile                   # Docker container
├── docker-compose.yaml         # Local development
├── requirements.txt            # Python dependencies
└── k8s/                        # Kubernetes manifests
```

---

## API Endpoints

### 1. Authentication Endpoints (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login with email/password | No |
| POST | `/refresh` | Refresh access token | No |
| POST | `/logout` | Logout current user | Yes |
| GET | `/me` | Get current user info | Yes |

**Request/Response Examples:**

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@example.com&password=password123"

# Response (Token)
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### 2. Organization Endpoints (`/api/v1/organizations`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/` | Create organization | Yes | admin |
| GET | `/` | List organizations | Yes | all |
| GET | `/{id}` | Get organization | Yes | all |
| PUT | `/{id}` | Update organization | Yes | admin |
| GET | `/{id}/stats` | Get organization stats | Yes | all |

---

### 3. Waste Management Endpoints (`/api/v1/waste`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create waste record + calculate credits | Yes |
| GET | `/` | List waste records | Yes |
| GET | `/{id}` | Get waste record | Yes |
| PUT | `/{id}` | Update waste record | Yes |
| POST | `/calculate` | Calculate credits without saving | Yes |

**Example - Create Waste Record:**

```bash
curl -X POST http://localhost:8000/api/v1/waste/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "uuid-here",
    "waste_type": "plastic",
    "plastic_type": "PET",
    "source": "collection_center",
    "collection_date": "2024-01-15T10:00:00Z",
    "quantity": 1000.0,
    "unit": "kg",
    "processing_method": "recycling"
  }'
```

---

### 4. Biochar Endpoints (`/api/v1/biochar`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create biochar record + calculate credits | Yes |
| GET | `/` | List biochar records | Yes |
| GET | `/{id}` | Get biochar record | Yes |
| POST | `/calculate` | Calculate credits without saving | Yes |

---

### 5. Carbon Credit Endpoints (`/api/v1/carbon-credits`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List carbon credits | Yes |
| GET | `/{id}` | Get carbon credit | Yes |
| GET | `/serial/{number}` | Get by serial number | Yes |
| POST | `/{id}/retire` | Retire carbon credit | Yes |
| GET | `/stats/summary` | Get credit statistics | Yes |

---

## Authentication

### JWT Token Flow

1. **Register** - Create new user account
2. **Login** - Get access + refresh tokens
3. **Use Access Token** - Include in API requests
4. **Refresh** - Use refresh token to get new access token

### Token Configuration

```python
# config.py
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"
```

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| admin | Full access to all resources |
| organization_admin | Manage organization, create credits |
| verifier | Verify carbon credits |
| user | View and create records |
| viewer | Read-only access |

---

## Carbon Calculation Engine

The formula engine implements carbon credit calculations based on `formula.md`:

### 1. General Carbon Credit Formula

```
CC = (E_baseline - E_project) × Q / 1000
```

Where:
- CC = Carbon Credits (tCO2e)
- E_baseline = Baseline emissions
- E_project = Project emissions
- Q = Quantity processed

### 2. Plastic Waste Formulas

| Plastic Type | Formula |
|--------------|---------|
| PET | CC = (EF_PETlandfill - EF_PETrecycling) × W / 1000 |
| HDPE | CC = (EF_HDPEdisposal - EF_HDPErecycling) × W / 1000 |
| PVC | CC = (EF_PVCincineration - EF_PVCrecycling) × W / 1000 |
| ... | ... |

### 3. Agricultural Waste Formulas

| Waste Type | Formula |
|------------|---------|
| Crop Residue | CC = (EF_burning - EF_mulching) × W / 1000 |
| Rice Straw | CC = (EF_strawburning - EF_biochar) × W / 1000 |
| Composting | CC = (EF_landfill - EF_compost) × W / 1000 |

### 4. Biochar Formula

```
CC = (C_captured + EF_soilimprovement) × W / 1000
```

### Using the Formula Engine

```python
from app.formula_engine.base import formula_engine, CalculationInput

# Calculate waste credits
result = formula_engine.calculate_waste_credit(
    waste_type="plastic",
    plastic_type="PET",
    quantity=1000,
    unit="kg",
    processing_method="recycling"
)

print(result.carbon_credits_generated)
print(result.emissions_reduced)
```

---

## Database Models

### User Model
```python
- id: UUID (primary key)
- email: str (unique)
- username: str (unique)
- hashed_password: str
- full_name: str
- role: str (admin, user, verifier, etc.)
- organization_id: UUID (foreign key)
- is_active: bool
- created_at: datetime
```

### Organization Model
```python
- id: UUID
- name: str
- slug: str (unique)
- organization_type: str
- total_carbon_credits: float
- total_waste_processed: float
- total_emissions_reduced: float
- is_verified: bool
```

### WasteRecord Model
```python
- id: UUID
- organization_id: UUID
- waste_type: str (plastic, agricultural)
- plastic_type: str (PET, HDPE, etc.)
- quantity: float
- unit: str (kg, tonnes)
- processing_method: str
- carbon_credit_generated: float
- baseline_emissions: float
- project_emissions: float
- emissions_reduced: float
- is_verified: bool
- verification_status: str
```

### BiocharRecord Model
```python
- id: UUID
- organization_id: UUID
- feedstock_type: str
- feedstock_quantity: float
- biochar_quantity: float
- biochar_yield_percentage: float
- carbon_content: float
- carbon_captured: float
- carbon_credit_generated: float
```

### CarbonCredit Model
```python
- id: UUID
- organization_id: UUID
- credit_type: str
- category: str
- serial_number: str (unique)
- quantity: float (tCO2e)
- status: str (pending, issued, retired)
- baseline_emissions: float
- project_emissions: float
- emissions_reduced: float
- is_retired: bool
- verification_level: str
```

---

## Services

### AuthService
- `register_user()` - Create new user
- `authenticate_user()` - Verify credentials
- `create_session()` - Create user session
- `refresh_access_token()` - Refresh JWT token

### WasteService
- `create_waste_record()` - Create + calculate credits
- `get_waste_records()` - List with filters
- `verify_waste_record()` - Mark as verified

### BiocharService
- `create_biochar_record()` - Create + calculate credits
- `get_biochar_records()` - List with filters

### CarbonCreditService
- `generate_credit_from_waste()` - Auto-generate from waste
- `generate_credit_from_biochar()` - Auto-generate from biochar
- `get_credits_by_organization()` - List credits
- `retire_credit()` - Retire credits

### VerificationService
- `create_verification_request()` - Create verification
- `approve_verification()` - Approve with scores
- `reject_verification()` - Reject with findings

---

## Configuration

### Environment Variables

```bash
# Application
APP_NAME="Carbon Credit Platform"
APP_VERSION="1.0.0"
ENVIRONMENT=development
DEBUG=true

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

---

## Docker & Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Docker Services
- **postgres** - PostgreSQL 16 database
- **redis** - Redis cache
- **app** - FastAPI application
- **celery** - Background task worker

### Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml

# Check pods
kubectl get pods
```

---

## CI/CD Pipeline

### Workflow Steps

1. **Lint** - Run Ruff, Black for code quality
2. **Test** - Python syntax check
3. **Build** - Build Docker image
4. **Deploy** - Deploy to production (main branch only)

### GitHub Secrets

Add these in repository Settings > Secrets:

| Secret | Description |
|--------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |

---

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL 16
- Redis

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/JadavMadhavkumar/CC_backend.git
cd CC_backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env with your settings

# 5. Run database migrations
python scripts/init_db.py

# 6. Start the server
uvicorn app.main:app --reload

# 7. Open API docs
# Visit http://localhost:8000/docs
```

### Using Docker

```bash
# Build and run
docker-compose up -d

# Access API
curl http://localhost:8000/health
```

---

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Testing

```bash
# Run unit tests
pytest app/tests/unit/ -v

# Run integration tests
pytest app/tests/integration/ -v

# Run with coverage
pytest --cov=app --cov-report=html
```

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`

---

## License

MIT License