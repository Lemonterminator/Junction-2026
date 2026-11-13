# syntax=docker/dockerfile:1
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends \
      git libgl1 libglib2.0-0 libusb-1.0-0 ffmpeg \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
# Isolated from Studio's PyTorch environment. CPU wheels avoid a CUDA download.
RUN uv pip install --system --torch-backend cpu -r /tmp/requirements.txt \
    && uv pip check --system \
    && mkdir -p /workspace /cache && chmod 1777 /cache
WORKDIR /workspace
CMD ["sleep", "infinity"]
