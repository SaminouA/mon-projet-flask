# Stage 1 : builder - installe les dependances
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/packages -r requirements.txt

# Stage 2 : image finale - uniquement le necessaire
FROM python:3.12-slim

WORKDIR /app

# Copier uniquement les dependances installees depuis le builder
COPY --from=builder /app/packages /app/packages

# Copier le code source
COPY src/ ./src/

# Installer curl pour le health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app/packages

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]
