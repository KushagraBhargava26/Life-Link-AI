# backend/Dockerfile
# LifeLink AI — Backend Service
# Architecture Reference: ARCHITECTURE.md Section 29 (Deployment Architecture)
#
# Python 3.11-slim — production-grade multi-stage build

# =============================================================================
# Stage 1: Builder — install dependencies
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies required for asyncpg and bcrypt compilation
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies into a separate prefix for clean copy
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime — minimal production image
# =============================================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser

# Expose internal port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
# --workers 1 for MVP single VPS deployment
# Increase to 4 in production with uvicorn workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
