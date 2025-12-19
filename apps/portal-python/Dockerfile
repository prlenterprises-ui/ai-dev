FROM python:3.11-slim

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy pyproject and install dependencies
COPY pyproject.toml .
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir .

# Copy source
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
