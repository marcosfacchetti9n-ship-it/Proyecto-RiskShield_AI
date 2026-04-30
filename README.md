# RiskShield AI

End-to-end transaction risk scoring platform using FastAPI, PostgreSQL, business rules and Machine Learning.

## Current Status

Phase 1 is implemented:

- Initial repository structure
- Minimal FastAPI backend
- `GET /health` endpoint
- Environment-based configuration with `pydantic-settings`
- Dockerfile for the backend
- Docker Compose with PostgreSQL
- Example environment file

The following modules are intentionally not implemented yet:

- Authentication
- Database models
- Alembic migrations
- Machine Learning
- Frontend
- Dashboard

## Project Structure

```text
backend/
  app/
    main.py
    core/
      config.py
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

## Next Phase

Phase 2 will add SQLAlchemy, database models, Alembic migrations and basic transaction endpoints.
