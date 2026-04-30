# RiskShield AI

End-to-end transaction risk scoring platform using FastAPI, PostgreSQL, business rules and Machine Learning.

## Current Status

Phases 1 to 9 are implemented:

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
- Admin registration and login
- JWT access tokens
- Protected transaction endpoints
- Protected dashboard metrics endpoints
- React + TypeScript administrative dashboard
- Dashboard charts and transaction analysis form
- Manual feedback workflow for reviewed transactions
- Expanded backend test suite for health, auth, transactions, risk engine, ML fallback, dashboard and feedback
- Frontend production build verification

## Project Structure

```text
backend/
  app/
    main.py
    core/
      config.py
      security.py
    db/
      database.py
      models.py
      session.py
    auth/
      router.py
      schemas.py
      service.py
    dashboard/
      router.py
      schemas.py
      service.py
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
      0004_add_transaction_feedback.py
  tests/
    conftest.py
    test_auth.py
    test_dashboard.py
    test_feedback.py
    test_health.py
    test_risk_engine.py
    test_transactions.py
  alembic.ini
  Dockerfile
  pytest.ini
  requirements.txt

docker-compose.yml
.env.example
.gitignore
README.md

frontend/
  src/
    api/
      auth.ts
      client.ts
      dashboard.ts
      transactions.ts
    components/
      DecisionBadge.tsx
      FeedbackBadge.tsx
      Layout.tsx
      MetricCard.tsx
      ProtectedRoute.tsx
      RiskBadge.tsx
      TransactionTable.tsx
    pages/
      DashboardPage.tsx
      LoginPage.tsx
      TransactionDetailPage.tsx
      TransactionsPage.tsx
    types/
      auth.ts
      dashboard.ts
      transaction.ts
    App.tsx
    index.css
    main.tsx
  Dockerfile
  package.json
  vite.config.ts
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

Set a strong `SECRET_KEY` in `.env`. You can generate one with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Start the services:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

The frontend will be available at:

```text
http://localhost:5173
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

## Environment Variables

Required auth variables:

```text
SECRET_KEY=replace_with_a_long_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`SECRET_KEY` must come from your local environment or `.env`; do not commit real secrets.

Frontend variable:

```text
VITE_API_BASE_URL=http://localhost:8000
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

Transaction endpoints require a Bearer token.

Register an admin user:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "StrongPass123"
  }'
```

Login:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "StrongPass123"
  }'
```

Use the returned `access_token` as a Bearer token.

Create a transaction:

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
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
curl "http://localhost:8000/transactions?limit=50&offset=0" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Analyze and persist a transaction:

```bash
curl -X POST http://localhost:8000/transactions/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
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

Add manual review feedback:

```bash
curl -X PATCH http://localhost:8000/transactions/TX-001/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "feedback_label": "confirmed_fraud",
    "feedback_notes": "Confirmed after manual review."
  }'
```

Allowed `feedback_label` values:

- `confirmed_fraud`
- `false_positive`
- `legitimate`

Example response excerpt:

```json
{
  "transaction_id": "TX-001",
  "feedback_label": "confirmed_fraud",
  "feedback_notes": "Confirmed after manual review.",
  "feedback_created_at": "2026-04-30T15:20:00Z",
  "feedback_updated_at": "2026-04-30T15:20:00Z"
}
```

## Dashboard API

Dashboard endpoints require a Bearer token.

Get global metrics:

```bash
curl http://localhost:8000/dashboard/metrics \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Example response:

```json
{
  "total_transactions": 120,
  "risk_level_counts": {
    "LOW": 70,
    "MEDIUM": 35,
    "HIGH": 15
  },
  "decision_counts": {
    "APPROVE": 70,
    "REVIEW": 35,
    "BLOCK": 15
  },
  "blocked_rate": 0.125,
  "average_final_score": 0.42,
  "model_available_rate": 0.95,
  "feedback_counts": {
    "confirmed_fraud": 10,
    "false_positive": 3,
    "legitimate": 20,
    "unreviewed": 87
  }
}
```

Metrics:

- `blocked_rate`: blocked transactions divided by total transactions.
- `average_final_score`: average persisted final score (`risk_score`).
- `model_available_rate`: transactions analyzed with ML available divided by total transactions.
- `feedback_counts`: manual review totals by feedback label plus unreviewed transactions.

Get recent transactions:

```bash
curl "http://localhost:8000/dashboard/recent-transactions?limit=10" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Get country risk distribution:

```bash
curl http://localhost:8000/dashboard/country-risk \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Get merchant category risk distribution:

```bash
curl http://localhost:8000/dashboard/category-risk \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Frontend

Install frontend dependencies:

```bash
cd frontend
npm install
```

Run the frontend locally:

```bash
npm run dev
```

Build the frontend:

```bash
npm run build
```

Run the full stack with Docker:

```bash
docker compose up --build
```

Frontend routes:

- `/login`: admin login
- `/dashboard`: metrics, charts and recent transactions
- `/transactions`: transaction table and analysis form
- `/transactions/:id`: transaction detail view with manual feedback controls

Manual feedback is available from a transaction detail page. Open a transaction from the table, choose the review label, add optional notes and save the feedback.

Future screenshots to add:

- Login screen
- Dashboard metrics overview
- Transaction analysis form with a HIGH risk result
- Transaction detail with rule, ML and feedback data

## Tests

The backend test suite uses an in-memory SQLite database configured in `backend/tests/conftest.py`. Each test starts from a clean schema, so tests do not depend on manual data from your local PostgreSQL database.

Build the API image after changing tests:

```bash
docker compose build api
```

Run backend tests:

```bash
docker compose run --rm api pytest
```

Run backend tests with verbose output:

```bash
docker compose run --rm api pytest -v
```

The backend suite covers:

- Health check response
- Admin registration, duplicate email validation, login and `/auth/me`
- Protected transaction creation and listing
- Invalid transaction payload validation
- Rule-based risk decisions and score bounds
- ML score combination and rule-only fallback
- Dashboard metrics and grouped risk summaries
- Feedback updates, invalid labels, missing transactions and persistence

Build the frontend:

```bash
cd frontend
npm run build
```

Recommended checks before pushing:

```bash
docker compose build api
docker compose run --rm api pytest
cd frontend
npm run build
```

## Next Phase

Phase 10 will polish the professional README and portfolio documentation.
