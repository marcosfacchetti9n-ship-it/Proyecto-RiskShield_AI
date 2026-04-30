# RiskShield AI

End-to-end transaction risk scoring platform using FastAPI, PostgreSQL, business rules and Machine Learning.

## Current Status

Phases 1 to 4 are implemented:

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
- Synthetic transaction dataset generation
- Scikit-learn training pipeline
- Optional ML model loading with rule-based fallback
- Final risk score combining rules and ML

The following modules are intentionally not implemented yet:

- Authentication
- Frontend
- Dashboard

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
    ml/
      generate_dataset.py
      train_model.py
      model.py
      data/
  alembic/
    versions/
      0001_initial_schema.py
      0002_add_main_factors.py
      0003_add_ml_score_fields.py
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

## Machine Learning Model

Generate the synthetic dataset:

```bash
docker compose run --rm api python app/ml/generate_dataset.py
```

The dataset is saved to:

```text
backend/app/ml/data/synthetic_transactions.csv
```

Train the model:

```bash
docker compose run --rm api python app/ml/train_model.py
```

The trained model is saved to:

```text
backend/app/ml/model.joblib
```

Generated datasets and model files are ignored by Git. If the model file does not exist, the API still works using only the rule-based Risk Engine.

After training, recreate the API container so it loads the model:

```bash
docker compose up -d --force-recreate api
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
  "rule_score": 1.0,
  "ml_score": 0.81,
  "final_score": 0.924,
  "risk_level": "HIGH",
  "decision": "BLOCK",
  "main_factors": [
    "High transaction amount",
    "Transaction hour between 00:00 and 05:00",
    "High-risk merchant category: gambling",
    "Unknown device"
  ],
  "model_available": true
}
```

## Tests

Run unit tests:

```bash
docker compose run --rm api python -m pytest
```

## Next Phase

Phase 5 will add JWT authentication and protect administrative endpoints.
