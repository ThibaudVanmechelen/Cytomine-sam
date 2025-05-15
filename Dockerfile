# === BUILD STAGE ===
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgl1 libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

COPY src ./src    

# === FINAL STAGE ===
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY src ./src
COPY weights ./weights
COPY configs ./configs

EXPOSE 6000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "6000"]