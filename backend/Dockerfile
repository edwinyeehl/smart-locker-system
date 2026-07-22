FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install python dependencies into virtual environment via uv
RUN uv sync --frozen --no-cache

# Copy application source code and migrations
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
