FROM python:3.12-slim
WORKDIR /app
# Dependances d'abord (cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Code source
COPY src/ ./src/
# Health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
CMD curl -f http://localhost:5000/health || exit 1
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]
