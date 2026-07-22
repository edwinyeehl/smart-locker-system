# Smart Locker System - Backend

For full system architecture, docker setup, tiered pricing documentation, and future scope considerations, please see the primary root **[README.md](../README.md)**.

## Quick Start

### Start Local Development Server
```bash
cd backend
uv run alembic upgrade head
uv run fastapi dev
```

Visit API Documentation: http://localhost:8000/docs

### Run Pytest Suite
```bash
uv run pytest
```
