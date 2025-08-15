FROM python:3.13-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies in a virtual environment
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY . .

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM python:3.13-slim AS production

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create non-root user with home directory
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from build stage
COPY --from=base --chown=appuser:appuser /app /app

# Create cache directory and set permissions
RUN mkdir -p /home/appuser/.cache && chown -R appuser:appuser /home/appuser/.cache

# Switch to non-root user
USER appuser

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD uv run python -c "import requests; requests.get('http://localhost:8000/docs')" || exit 1

ENV WEBHOOK_SECRET=change-me \
    REPO_URL= \
    REPO_BRANCH=main


    # Start the application
CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]



