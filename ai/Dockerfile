# ai/Dockerfile
# LifeLink AI — AI Inference Service
# Architecture Reference: ARCHITECTURE.md Section 17 (AI Architecture) & Section 29 (Deployment Architecture)
#
# Python 3.11-slim — production-grade multi-stage build

# =============================================================================
# Stage 1: Builder — install dependencies
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies required for compilation
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies into a separate prefix
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime — minimal production image
# =============================================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser

# Expose internal port for the AI service
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start command
# Runs on port 8001 as specified in ARCHITECTURE.md
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
