FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY challenge/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY challenge/ .

# Non-root
RUN useradd -m -u 1000 nibbles && chown -R nibbles:nibbles /app
USER nibbles

# Run
CMD ["python", "app.py"]
