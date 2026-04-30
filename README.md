# RiskShield AI

End-to-end transaction risk scoring platform using FastAPI, PostgreSQL, business rules and Machine Learning.

RiskShield AI is a professional portfolio project that simulates how a financial risk platform can receive transactions, calculate risk, suggest a decision and expose results through an administrative dashboard. It is intentionally built as a complete application, not as a standalone ML notebook.

## Problem

Financial teams need to review transactions quickly, consistently and with enough context to understand why a transaction was approved, blocked or sent to manual review. A useful risk system must combine API design, persistence, authentication, business logic, Machine Learning, observability through metrics and a clear admin experience.

RiskShield AI demonstrates that full workflow:

- Admin users authenticate with JWT.
- Transactions are submitted through a REST API or React dashboard.
- A rule-based Risk Engine calculates deterministic risk signals.
- An optional scikit-learn model contributes an ML risk score.
- The system combines both scores into a final decision.
- Results are persisted in PostgreSQL.
- Dashboard metrics summarize operational risk.
- Admin users can add manual feedback for future model improvement.

## Features

- FastAPI backend with modular routers, schemas and services
- PostgreSQL persistence with SQLAlchemy models
- Alembic database migrations
- JWT authentication for protected admin endpoints
- Rule-based risk scoring with readable main factors
- Optional ML scoring with scikit-learn and joblib
- Rule-only fallback when the ML model is not available
- Synthetic dataset generation for local ML experimentation
- Dashboard API for metrics, recent transactions and grouped risk summaries
- React + TypeScript dashboard with Tailwind CSS, Axios and Recharts
- Manual feedback workflow: confirmed fraud, false positive and legitimate
- Docker Compose for local development
- Backend tests for health, auth, transactions, risk engine, dashboard and feedback
- Frontend production build verification

## Tech Stack

**Backend**

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT with python-jose
- passlib + bcrypt
- Docker

**Machine Learning**

- pandas
- numpy
- scikit-learn
- joblib
- Synthetic transaction dataset

**Frontend**

- React
- TypeScript
- Vite
- Tailwind CSS
- Axios
- Recharts
- React Router

**Infrastructure and Quality**

- Docker Compose
- Environment variables with `.env`
- pytest
- In-memory SQLite test database
- Git-ready structure for portfolio presentation

## Architecture

```text
Client
  -> React Dashboard
  -> FastAPI API
  -> Auth / Transactions / Dashboard modules
  -> Risk Engine
  -> Optional ML Model
  -> PostgreSQL
```

**React Dashboard**

Provides the admin interface for login, metrics, transaction analysis, transaction detail and manual feedback.

**FastAPI API**

Exposes REST endpoints, validates requests with Pydantic and separates concerns by module: auth, transactions, risk, dashboard and ML.

**Risk Engine**

Combines deterministic business rules with an optional ML model. Rules are kept separate from API routers so they can be tested independently.

**ML Model**

Uses a scikit-learn pipeline trained on synthetic transaction data. If the model file is missing, the backend continues working with rule-based scoring.

**PostgreSQL**

Stores users, transactions, scores, decisions, risk factors and manual feedback.

## Flow

1. Admin logs in and receives a JWT access token.
2. Admin submits a transaction from the dashboard or API.
3. Backend validates and normalizes the transaction payload.
4. Risk Engine calculates `rule_score` from business rules.
5. Backend calculates `ml_score` if the trained model is available.
6. System combines scores into `final_score`.
7. API returns `risk_level`, `decision` and `main_factors`.
8. Transaction and result are persisted in the database.
9. Dashboard metrics update from persisted data.
10. Admin can add manual feedback for future model improvement.

## Risk Decisions

Risk levels:

- `LOW`: score lower than `0.35`
- `MEDIUM`: score from `0.35` to `0.70`
- `HIGH`: score greater than `0.70`

Decisions:

- `LOW` -> `APPROVE`
- `MEDIUM` -> `REVIEW`
- `HIGH` -> `BLOCK`

Final score:

```text
final_score = 0.60 * rule_score + 0.40 * ml_score
```

If the ML model is unavailable:

```text
final_score = rule_score
```

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
  tests/
  alembic.ini
  Dockerfile
  pytest.ini
  requirements.txt

frontend/
  src/
    api/
    components/
    pages/
    types/
    App.tsx
    main.tsx
  Dockerfile
  package.json

docker-compose.yml
.env.example
.gitignore
LICENSE
README.md
```

## Screenshots

Screenshots will be added after final UI review.

Planned screenshots:

- Login
- Dashboard
- Transactions
- Transaction Detail
- Feedback

## Environment Variables

Copy the example file before running locally:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Set a strong local secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Main variables:

```text
APP_NAME=RiskShield AI
ENVIRONMENT=development

BACKEND_PORT=8000
FRONTEND_PORT=5173

POSTGRES_USER=riskshield
POSTGRES_PASSWORD=change_me_locally
POSTGRES_DB=riskshield_ai
POSTGRES_PORT=5432

DATABASE_URL=postgresql+psycopg://riskshield:change_me_locally@postgres:5432/riskshield_ai

SECRET_KEY=replace_with_a_long_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

ML_MODEL_PATH=app/ml/model.joblib

VITE_API_BASE_URL=http://localhost:8000
VITE_API_URL=http://localhost:8000
```

`SECRET_KEY` must be generated locally and never committed.

## Run With Docker

Build and start all services:

```bash
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432`

Stop services:

```bash
docker compose down
```

Stop services and remove volumes:

```bash
docker compose down -v
```

## Render Deployment Notes

Backend service:

```text
Environment: Docker
Root Directory: backend
Dockerfile Path: Dockerfile
```

Leave the Docker command unset unless you intentionally need to override it. The backend image uses `backend/start.sh`, which runs:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

This is useful on Render Free because the service may not provide an interactive shell for running migrations manually.

Frontend service:

```text
Environment: Static Site
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

## Database Migrations

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Run migrations:

```bash
docker compose run --rm api alembic upgrade head
```

Check current migration:

```bash
docker compose run --rm api alembic current
```

## Machine Learning

Generate a synthetic dataset:

```bash
docker compose run --rm api python app/ml/generate_dataset.py
```

Dataset output:

```text
backend/app/ml/data/synthetic_transactions.csv
```

Train the ML model:

```bash
docker compose run --rm api python app/ml/train_model.py
```

Model output:

```text
backend/app/ml/model.joblib
```

The generated dataset and model are ignored by Git. They are reproducible artifacts, so the repository stays lightweight while still documenting the full training flow.

After training, recreate the API container so it reloads the model:

```bash
docker compose up -d --force-recreate api
```

## Frontend Usage

Install dependencies:

```bash
cd frontend
npm install
```

Run locally:

```bash
npm run dev
```

Build production assets:

```bash
npm run build
```

Main routes:

- `/login`: admin login
- `/dashboard`: metrics, charts and recent transactions
- `/transactions`: transaction table and analysis form
- `/transactions/:id`: transaction detail and manual feedback

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

Build the frontend:

```bash
cd frontend
npm run build
```

Current test coverage includes:

- Health check
- Admin registration, duplicate email validation, login and `/auth/me`
- Protected transaction creation and listing
- Invalid transaction payload validation
- Rule-based risk decisions and score bounds
- ML score combination and rule-only fallback
- Dashboard metrics and grouped risk summaries
- Feedback updates, invalid labels, missing transactions and persistence

## Main API Endpoints

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| `GET` | `/health` | Service health check | No |
| `POST` | `/auth/register` | Register admin user | No |
| `POST` | `/auth/login` | Login and receive JWT | No |
| `GET` | `/auth/me` | Current authenticated user | Yes |
| `POST` | `/transactions` | Create transaction | Yes |
| `POST` | `/transactions/analyze` | Analyze and persist transaction | Yes |
| `GET` | `/transactions` | List transactions | Yes |
| `PATCH` | `/transactions/{transaction_id}/feedback` | Add manual feedback | Yes |
| `GET` | `/dashboard/metrics` | Dashboard metrics | Yes |
| `GET` | `/dashboard/recent-transactions` | Recent transactions | Yes |
| `GET` | `/dashboard/country-risk` | Risk grouped by country | Yes |
| `GET` | `/dashboard/category-risk` | Risk grouped by merchant category | Yes |

## API Examples

### Register Admin

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "StrongPass123"
  }'
```

Example response:

```json
{
  "id": 1,
  "email": "admin@example.com",
  "is_active": true,
  "created_at": "2026-04-30T12:00:00Z"
}
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "StrongPass123"
  }'
```

Example response:

```json
{
  "access_token": "<JWT_ACCESS_TOKEN>",
  "token_type": "bearer"
}
```

### Create Transaction

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
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

### Analyze Transaction

```bash
curl -X POST http://localhost:8000/transactions/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
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

Example response excerpt:

```json
{
  "transaction_id": "TX-001",
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

### Add Feedback

```bash
curl -X PATCH http://localhost:8000/transactions/TX-001/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -d '{
    "feedback_label": "confirmed_fraud",
    "feedback_notes": "Confirmed after manual review."
  }'
```

Allowed labels:

- `confirmed_fraud`
- `false_positive`
- `legitimate`

Example response excerpt:

```json
{
  "transaction_id": "TX-001",
  "feedback_label": "confirmed_fraud",
  "feedback_notes": "Confirmed after manual review.",
  "feedback_created_at": "2026-04-30T12:30:00Z",
  "feedback_updated_at": "2026-04-30T12:30:00Z"
}
```

### Dashboard Metrics

```bash
curl http://localhost:8000/dashboard/metrics \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
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

## Technical Decisions

- **FastAPI over notebook-only ML**: the project demonstrates production-style API delivery, not just offline modeling.
- **Rules plus ML**: deterministic rules keep the system explainable, while ML adds a probabilistic signal.
- **ML fallback**: the API remains usable even when `model.joblib` is missing.
- **Modular backend**: routers handle HTTP, services handle business flow, schemas validate data and models persist state.
- **Alembic migrations**: database changes are versioned and reproducible.
- **JWT auth**: admin endpoints are protected while `/health` and docs remain public.
- **Synthetic data**: avoids external dependencies and keeps the project reproducible.
- **Feedback storage**: manual review labels are persisted for future retraining workflows.
- **SQLite for tests**: fast, isolated tests without depending on local PostgreSQL data.
- **Generated artifacts ignored**: datasets and models can be rebuilt locally, keeping Git history lightweight.

## Limitations

- The ML dataset is synthetic and does not represent real financial fraud distributions.
- The ML model is intentionally simple for clarity.
- Manual feedback is stored but does not trigger automatic retraining yet.
- There are no advanced user roles.
- Access tokens do not use refresh tokens yet.
- Dashboard filters and pagination are intentionally basic.
- The project is configured for local development, not hardened production deployment.

## Future Improvements

- Add SHAP or another explainability layer for ML predictions
- Retrain the ML model using stored manual feedback
- Add admin roles and permissions
- Add refresh tokens and session management
- Improve pagination and server-side filters
- Add CI/CD with GitHub Actions
- Add production deployment configuration
- Add monitoring, structured logs and metrics
- Add frontend automated tests
- Add screenshot assets after final UI review

## Useful Commands

```bash
# Start full stack
docker compose up --build

# Stop full stack
docker compose down

# Run database migrations
docker compose run --rm api alembic upgrade head

# Generate synthetic ML dataset
docker compose run --rm api python app/ml/generate_dataset.py

# Train ML model
docker compose run --rm api python app/ml/train_model.py

# Run backend tests
docker compose run --rm api pytest

# Run verbose backend tests
docker compose run --rm api pytest -v

# Build frontend
cd frontend
npm run build
```

## What I Learned

Building RiskShield AI reinforced practical skills across the full application lifecycle:

- Designing REST APIs with clear contracts and validation
- Separating responsibilities across routers, services, schemas and domain logic
- Combining backend business rules with an ML prediction pipeline
- Handling JWT authentication and protected admin workflows
- Persisting data safely with SQLAlchemy, PostgreSQL and Alembic
- Building a React dashboard that consumes real APIs
- Using Docker Compose for reproducible local development
- Writing backend tests with isolated fixtures and clean test data

## Project Status

RiskShield AI is complete as a portfolio-ready MVP. It includes backend, database, migrations, authentication, risk scoring, ML training flow, dashboard API, frontend dashboard, manual feedback and automated backend tests.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
