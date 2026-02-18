FROM python:3.14-slim AS base

# Install git (required for uv to fetch git dependencies)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

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


FROM python:3.14-slim AS production

# Install git for content cloning
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create non-root user with home directory
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from build stage
COPY --from=base --chown=appuser:appuser /app /app

# Switch to non-root user
USER appuser

EXPOSE 33000

CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0", "--port", "33000", "--entrypoint", "personal_site.main:app"]



