# Carbon Credit Platform Backend

Production-grade backend for Carbon Credit Management Platform built with Python FastAPI.

## Features

- **Carbon Credit Calculations** - Dynamic formula engine based on plastic waste, agricultural waste, and biochar formulas
- **Waste Management** - Track waste collection and processing with automatic carbon credit generation
- **Biochar Tracking** - Monitor biochar production and soil application carbon benefits
- **Verification System** - Multi-level verification workflow for carbon credits
- **Multi-tenant Support** - Organization-based access control
- **Security** - JWT authentication, RBAC, rate limiting, security headers

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.12+
- **Database**: PostgreSQL (async with SQLAlchemy 2.0)
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT with refresh tokens
- **Caching**: Redis
- **Task Queue**: Celery
- **Testing**: Pytest

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Update .env with your settings

# Run database migrations
python scripts/init_db.py

# Start the server
uvicorn app.main:app --reload
```

### Using Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

### Organizations
- `POST /api/v1/organizations` - Create organization
- `GET /api/v1/organizations` - List organizations
- `GET /api/v1/organizations/{id}` - Get organization
- `GET /api/v1/organizations/{id}/stats` - Get organization stats

### Waste Management
- `POST /api/v1/waste/` - Create waste record
- `GET /api/v1/waste/` - List waste records
- `POST /api/v1/waste/calculate` - Calculate carbon credits

### Biochar
- `POST /api/v1/biochar/` - Create biochar record
- `GET /api/v1/biochar/` - List biochar records
- `POST /api/v1/biochar/calculate` - Calculate carbon credits

### Carbon Credits
- `GET /api/v1/carbon-credits/` - List carbon credits
- `GET /api/v1/carbon-credits/stats/summary` - Get statistics
- `POST /api/v1/carbon-credits/{id}/retire` - Retire credits

## Carbon Calculation Formulas

The platform implements formulas from `formula.md`:

### Plastic Waste
- General Plastic: `CC = (EF_landfill - EF_recycling) × W / 1000`
- PET, HDPE, PVC, LDPE, PP, PS, ABS, PC, Nylon, PU, EPS variants

### Agricultural Waste
- General: `CC = (EF_openburning - EF_sustainablemanagement) × W / 1000`
- Crop Residue, Rice Straw, Sugarcane Bagasse, Corn Stover, etc.

### Biochar
- `CC = (C_captured + EF_soilimprovement) × W / 1000`

## Testing

```bash
# Run unit tests
pytest app/tests/unit/

# Run integration tests
pytest app/tests/integration/

# Run all tests with coverage
pytest --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/   # API routes
│   ├── core/               # Config, DB, Security
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── formula_engine/     # Carbon calculations
│   ├── middleware/        # Custom middleware
│   ├── workers/           # Celery tasks
│   └── tests/             # Test suite
├── docker/                 # Docker configs
├── k8s/                   # Kubernetes manifests
└── scripts/               # Utility scripts
```

## License

MIT