# Production image for the DevTrack API.
#
# Migrations are NOT run here — see the `migrate` service in the repo root
# docker-compose.yml / README for the deliberate, explicit migration step.
# Running `alembic upgrade head` silently on every container start makes
# failures hard to diagnose and can race multiple replicas; a dedicated step
# is more predictable.

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Only runtime dependencies — requirements-dev.txt (pytest, ruff) never
# ships in the image.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
