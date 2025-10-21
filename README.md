# Flight Search API - Amo Promo Challenge

A Django REST API that caches airport data and searches flights across multiple airlines, calculating all possible round-trip combinations with prices and metrics. It can be used as a backend for a flight search application or integrated with it´s own frontend.

## What it does

1. **Imports and caches airports** from an external API into SQLite
2. **Searches flights** by calling Mock Airlines API twice (outbound + inbound)
3. **Calculates everything**: fees, distances (Haversine), cruise speed, cost per km
4. **Generates all combinations** of outbound × inbound flights, sorted by price

## Quick Start

```bash
# Clone and enter
git clone https://github.com/ReformedTheo/desafio-amopromo.git
cd desafio-amopromo-1

# Create .env file (sent via email)
# Then start
docker compose up -d

# Run migrations
docker compose exec backend python manage.py migrate

# Import airports
docker compose exec backend python manage.py import_airports

# Run tests
docker compose exec backend python manage.py test core
```

API runs at `http://localhost:8000`
FRONTEND runs at `http://localhost:3000`

## Environment Variables

Create `.env` file:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

AIRPORT_DATA_URL=https://stub.amopromo.com/air/airports
API_USER=demo
API_PASSWORD=swnvlD

MOCK_API_BASE_URL=https://stub-850169372117.us-central1.run.app/air/search
MOCK_API_KEY=pzrvlDwoCwlzrWJmOzviqvOWtm4dkvuc
MOCK_API_USER=demo
MOCK_API_PASSWORD=swnvlD
```

## API Endpoints

### Search Flights (Protected)
```bash
curl -H "Authorization: Token pzrvlDwoCwlzrWJmOzviqvOWtm4dkvuc" \
  "http://localhost:8000/api/flights_integration/search/?from=GRU&to=GIG&departureDate=2025-12-01&returnDate=2025-12-10"
```

Returns all possible flight combinations with calculated prices and metadata.

### List Airports
```bash
curl http://localhost:8000/api/airports/
```

### Import Airports
```bash
curl -X POST http://localhost:8000/api/airports/import/ \
  -d "user=demo&password=swnvlD"
```

### View Logs (Protected)
```bash
curl -H "Authorization: Token pzrvlDwoCwlzrWJmOzviqvOWtm4dkvuc" \
  "http://localhost:8000/api/logs/?level=ERROR"
```

## Tech Stack

- Python 3.11 + Django 5.2
- SQLite (easily swappable)
- Docker + Docker Compose
- Requests for API calls
- Database logging (no files)

## How It Works

**Price calculation**: Fee is 10% of fare or R$40 (whichever is higher), then fare + fee = total

**Distance**: Haversine formula using lat/lon coordinates

**Metadata**: cruise_speed = distance / flight_duration, cost_per_km = fare / distance

**Combinations**: Cartesian product of all outbound × inbound options, sorted by total price ascending

## Project Structure

```
backend/
  core/
    models/           # Airport, ImportLog, ApplicationLog
    views/            # API endpoints
    services.py       # Business logic (Haversine, calculations, API calls)
    tests.py          # Unit tests
    management/commands/
      import_airports.py  # CLI: python manage.py import_airports
docker/              # Dockerfiles
docker-compose.yml   # Container orchestration
```

## Validations

- Origin ≠ Destination
- Airports must exist in database
- Departure date ≥ today
- Return date ≥ departure date

## Endpoints
- `GET /api/flights_integration/search/`: Search flights (token auth)
- `GET /api/airports/`: List cached airports
- `POST /api/airports/import/`: Import airports from external API (basic auth)
- `GET /api/logs/`: View application logs (token auth)

## Notes

- All code and comments in English
- Database logging instead of file logging for better querying
- Token auth using env variable
- Import logs track every airport sync
- React frontend included but optional

---

**Challenge**: [Amo Promo Backend Test](https://gist.github.com/billyninja/f54aaa57c20adc25bf90eaf3c2f14160)
