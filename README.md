# RiskShield AI

End-to-end transaction risk scoring platform using FastAPI, PostgreSQL, business rules and Machine Learning.

## Current Status

Phase 2 is implemented:

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

The following modules are intentionally not implemented yet:

- Authentication
- Machine Learning
- Frontend
- Dashboard
- Advanced risk scoring logic

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
  alembic/
    versions/
      0001_initial_schema.py
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

## Next Phase

Phase 3 will add the first version of the Risk Engine using business rules only.
