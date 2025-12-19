FROM python:3.11-slim

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy pyproject and install dependencies
COPY pyproject.toml .
COPY pyproject.lock . 2>/dev/null || true
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir .

# Copy source
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
