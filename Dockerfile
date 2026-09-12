# Aletheia AI — Dockerfile
# Multi-stage build for a small, reproducible image.

FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels .

# ── runtime ─────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN groupadd -r aletheia && useradd -r -g aletheia -d /app -s /sbin/nologin aletheia

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

COPY --chown=aletheia:aletheia . /app

RUN mkdir -p /app/data && chown -R aletheia:aletheia /app

USER aletheia

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2); sys.exit(0)" || exit 1

ENTRYPOINT ["python", "-m", "aletheia.api.server"]
