FROM python:3.12-slim

ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./
COPY src ./src

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi

COPY weights ./weights
COPY configs ./configs

EXPOSE 6000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "6000"]