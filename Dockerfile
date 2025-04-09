# === Build Stage ===
FROM python:3.12-slim as builder

ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential libgl1 libglib2.0-0 \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY src ./src

RUN poetry config virtualenvs.create false

RUN poetry install --no-dev --no-interaction --no-ansi

# === Final Stage ===
FROM python:3.12-slim

ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app /app

COPY weights ./weights
COPY configs ./configs

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]