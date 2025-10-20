FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl gcc libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /backend

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy project metadata first for dependency install caching
COPY pyproject.toml poetry.lock* /backend/

# Configure poetry to not create venvs and install
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy application code
COPY . /backend/

# Collect static files and run migrations on container start, then run gunicorn
ENV PORT=8000
EXPOSE 8000

CMD python manage.py migrate --noinput \
    && gunicorn import_airports.wsgi:application --bind 0.0.0.0:8000 --workers 3
