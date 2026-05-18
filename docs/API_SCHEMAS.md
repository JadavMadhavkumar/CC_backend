# API Schema Reference

## Authentication Schemas

### UserCreate
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "John Doe",
  "role": "user"
}
```

### Token Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

## Waste Management Schemas

### WasteRecordCreate
```json
{
  "organization_id": "uuid-string",
  "waste_type": "plastic",
  "plastic_type": "PET",
  "source": "collection_center",
  "collection_date": "2024-01-15T10:00:00Z",
  "quantity": 1000.0,
  "unit": "kg",
  "processing_method": "recycling",
  "location": "Warehouse A",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

### WasteRecordResponse
```json
{
  "id": "uuid-string",
  "organization_id": "uuid-string",
  "waste_type": "plastic",
  "plastic_type": "PET",
  "source": "collection_center",
  "collection_date": "2024-01-15T10:00:00Z",
  "quantity": 1000.0,
  "unit": "kg",
  "processing_method": "recycling",
  "carbon_credit_generated": 5.5,
  "baseline_emissions": 6400.0,
  "project_emissions": 800.0,
  "emissions_reduced": 5600.0,
  "is_verified": false,
  "verification_status": "pending",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### WasteCalculationRequest
```json
{
  "waste_type": "plastic",
  "plastic_type": "PET",
  "quantity": 1000,
  "unit": "kg",
  "processing_method": "recycling",
  "disposal_method_baseline": "landfill",
  "disposal_method_project": "recycling",
  "region": "US"
}
```

### WasteCalculationResponse
```json
{
  "formula_code": "CC_PLASTIC_WASTE",
  "formula_name": "Plastic Waste Recycling - PET",
  "baseline_emissions": 6400.0,
  "project_emissions": 800.0,
  "emissions_reduced": 5600.0,
  "carbon_credits_generated": 5.6,
  "unit": "tCO2e",
  "emission_factors_used": {
    "EF_PET_landfill": 6.4,
    "EF_PET_recycling": 0.8
  }
}
```

## Biochar Schemas

### BiocharRecordCreate
```json
{
  "organization_id": "uuid-string",
  "production_date": "2024-01-15T10:00:00Z",
  "feedstock_type": "wood",
  "feedstock_quantity": 1000.0,
  "feedstock_unit": "kg",
  "biochar_quantity": 300.0,
  "biochar_unit": "kg",
  "biochar_yield_percentage": 30.0,
  "carbon_content": 70.0,
  "pyrolysis_temperature": 500.0,
  "technology": "kiln",
  "application_site": "farm_field",
  "soil_type": "clay"
}
```

### BiocharCalculationResponse
```json
{
  "formula_code": "CC_BIOCHAR",
  "formula_name": "Biochar Production",
  "carbon_captured": 770.0,
  "soil_improvement_factor": 0.05,
  "total_carbon_credits": 0.775,
  "unit": "tCO2e",
  "calculations": {
    "biochar_yield_percentage": 30.0,
    "carbon_content_percentage": 70.0,
    "biochar_quantity": 300.0,
    "carbon_captured_kg": 770.0,
    "soil_carbon_enhancement": 38.5
  }
}
```

## Carbon Credit Schemas

### CarbonCreditResponse
```json
{
  "id": "uuid-string",
  "organization_id": "uuid-string",
  "credit_type": "waste_management",
  "category": "plastic",
  "sub_category": "PET",
  "vintage_year": 2024,
  "serial_number": "CC-20240115-A1B2C3D4",
  "quantity": 5.6,
  "unit": "tCO2e",
  "status": "generated",
  "baseline_emissions": 6400.0,
  "project_emissions": 800.0,
  "emissions_reduced": 5600.0,
  "verification_level": "pending",
  "is_retired": false,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### CarbonCreditStats
```json
{
  "total_credits": 1000.0,
  "pending_credits": 200.0,
  "issued_credits": 700.0,
  "retired_credits": 100.0,
  "verified_credits": 500.0,
  "credits_by_category": {
    "plastic": 600.0,
    "agricultural": 300.0,
    "biochar": 100.0
  },
  "credits_by_status": {
    "generated": 200.0,
    "issued": 700.0,
    "retired": 100.0
  }
}
```

## Organization Schemas

### OrganizationCreate
```json
{
  "name": "Acme Recycling Corp",
  "slug": "acme-recycling",
  "description": "Leading plastic waste recycler",
  "organization_type": "company",
  "registration_number": "RC-123456",
  "country": "USA",
  "industry": "Waste Management",
  "email": "contact@acme.com",
  "phone": "+1-555-0123"
}
```

### OrganizationStats
```json
{
  "total_carbon_credits": 5000.0,
  "total_waste_processed": 100000.0,
  "total_emissions_reduced": 50000.0,
  "waste_records_count": 150,
  "biochar_records_count": 25,
  "carbon_credits_count": 75,
  "pending_verifications": 5
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Incorrect email or password",
  "headers": {"WWW-Authenticate": "Bearer"}
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "Input should be greater than 0",
      "type": "value_error"
    }
  ]
}
```

### 429 Rate Limited
```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Query Parameters

### Pagination
```bash
GET /api/v1/waste/?skip=0&limit=100
```

### Filtering
```bash
GET /api/v1/waste/?waste_type=plastic&organization_id=uuid
GET /api/v1/biochar/?feedstock_type=wood
GET /api/v1/carbon-credits/?status=issued
```

### Sorting
```bash
# Add sorting parameter (implementation specific)
GET /api/v1/waste/?sort=-created_at
```

## Headers

### Required Headers
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Optional Headers
```http
X-Request-ID: uuid (for tracking)
Accept: application/json
```