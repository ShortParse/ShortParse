# Stage 1: Build dependencies and compile packages
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Compile requirements directly to globally readable /usr/local site-packages
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Clean, secure production runner
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime dependencies (e.g., PostgreSQL library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled packages from builder stage
COPY --from=builder /usr/local /usr/local

# Copy application source directories
COPY shortparse /app/shortparse
COPY main.py /app/main.py

# Create non-root system user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -u 10001 appuser

# Setup local storage directory permissions for SQLite fallback databases
RUN mkdir -p /app/storage && chown -R appuser:appgroup /app

# Switch context to secure non-root user account
USER 10001

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

# Health check probe hitting the FastAPI application status
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Launch the FastAPI app server
CMD ["uvicorn", "shortparse.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
