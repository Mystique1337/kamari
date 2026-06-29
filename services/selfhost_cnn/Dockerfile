# Standalone CPU CNN age server for self-hosting (no Modal, no GPU).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# CPU-only torch keeps the image small.
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY cnn_server.py .

ENV PORT=8001
CMD ["sh", "-c", "uvicorn cnn_server:app --host 0.0.0.0 --port ${PORT}"]
