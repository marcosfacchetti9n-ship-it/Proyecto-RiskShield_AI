# RiskShield AI

End-to-end transaction risk scoring platform using FastAPI, PostgreSQL, business rules and Machine Learning.

## Current Status

Phases 1 to 3 are implemented:

- Initial repository structure
- Minimal FastAPI backend
- `GET /health` endpoint
- Environment-based configuration with `pydantic-settings`
- Dockerfile for the backend
- Docker Compose with PostgreSQL
- Example environment file
- PostgreSQL connection with SQLAlchemy
- Initial `User` and `Transaction` models
- Alembic configuration
- Initial database migration
- Basic transaction create/list endpoints
- Rule-based Risk Engine
- Transaction analysis endpoint
- Persisted risk score, risk level, decision and main factors
- Unit tests for risk scoring rules

The following modules are intentionally not implemented yet:

- Authentication
- Frontend
- Dashboard
- Machine Learning-based scoring

## Project Structure

```text
backend/
  app/
    main.py
    core/
      config.py
    db/
      database.py
      models.py
      session.py
    transactions/
      router.py
      schemas.py
      service.py
    risk/
      engine.py
      explanations.py
      rules.py
      types.py
  alembic/
    versions/
      0001_initial_schema.py
      0002_add_main_factors.py
  tests/
    test_risk_engine.py
  alembic.ini
  Dockerfile
  requirements.txt

docker-compose.yml
.env.example
.gitignore
README.md
```

## Run Locally With Docker

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Start the services:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API docs:

```text
http://localhost:8000/docs
```

## Database Migrations

Build the backend image and start PostgreSQL:

```bash
docker compose build api
docker compose up -d postgres
```

Run Alembic migrations:

```bash
docker compose run --rm api alembic upgrade head
```

Check current migration:

```bash
docker compose run --rm api alembic current
```

## Health Check

Test the backend:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "RiskShield AI",
  "environment": "development"
}
```

## Transactions API

Create a transaction:

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR-001",
    "amount": 250000,
    "currency": "ARS",
    "country": "Argentina",
    "device": "mobile",
    "hour": 3,
    "merchant_category": "electronics"
  }'
```

List transactions:

```bash
curl "http://localhost:8000/transactions?limit=50&offset=0"
```

Analyze and persist a transaction:

```bash
curl -X POST http://localhost:8000/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR-001",
    "amount": 250000,
    "currency": "ARS",
    "country": "Argentina",
    "device": "unknown",
    "hour": 3,
    "merchant_category": "gambling"
  }'
```

The response includes:

```json
{
  "risk_score": 1.0,
  "risk_level": "HIGH",
  "decision": "BLOCK",
  "main_factors": [
    "High transaction amount",
    "Transaction hour between 00:00 and 05:00",
    "High-risk merchant category: gambling",
    "Unknown device"
  ]
}
```

## Tests

Run unit tests:

```bash
docker compose run --rm api python -m pytest
```

## Next Phase

Phase 4 will add the first Machine Learning model and combine its score with the rule-based engine.
