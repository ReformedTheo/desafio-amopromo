import os
import requests
from requests.auth import HTTPBasicAuth
from django.utils import timezone

import datetime
import math
from typing import Dict, Any, List

from .models.airport_model import Airport
from .models.import_log_model import ImportLogModel
from .utils.logging_utils import log_warning, log_error


MOCK_API_KEY = os.getenv("MOCK_API_KEY", "demo_key")
MOCK_API_BASE_URL = os.getenv("MOCK_API_BASE_URL")
MOCK_API_USER = os.getenv("MOCK_API_USER", "demo")
MOCK_API_PASSWORD = os.getenv("MOCK_API_PASSWORD", "swnvlD")
EARTH_RADIUS_KM = 6371.0

def import_airports_from_api(user=None, password=None):

    api_url = os.getenv("AIRPORT_DATA_URL")
    if user and password:
        api_user = user
        api_password = password
    else:
        api_user = os.getenv("API_USER")
        api_password = os.getenv("API_PASSWORD")

    if not api_url:
        raise ValueError("AIRPORT_DATA_URL environment variable is not set.")

    log_entry = ImportLogModel.objects.create(status=ImportLogModel.Status.FAILED)

    created_iata_list = []
    updated_iata_list = []

    try:
        response = requests.get(api_url, auth=HTTPBasicAuth(api_user, api_password), timeout=30)
        response.raise_for_status()
        
        data = response.json()
        airports_in_api = []

        for airport_data in data.values():
            iata_code = airport_data.get('iata')
            if not iata_code:
                continue
            
            airports_in_api.append(iata_code)

            # Create new airport or update existing one based on IATA code
            obj, created = Airport.objects.update_or_create(
                iata=iata_code,
                defaults={
                    'state': airport_data.get('state'),
                    'city': airport_data.get('city'),
                    'lat': airport_data.get('lat'),
                    'lon': airport_data.get('lon'),
                }
            )
            
            if created:
                created_iata_list.append(iata_code)
            else:
                updated_iata_list.append(iata_code)

        log_entry.status = ImportLogModel.Status.SUCCESS
        log_entry.details = f"Successfully processed {len(data)} airports."

    except requests.exceptions.RequestException as e:
        log_entry.details = f"Failed to fetch data from API: {str(e)}"
        log_warning('core.services', f"API request failed while importing airports: {str(e)}", {'error': str(e)})
    except Exception as e:
        log_entry.details = f"An unexpected error occurred: {str(e)}"
        log_error('core.services', f"Unexpected error during import_airports_from_api: {str(e)}", {'error': str(e)})
    
    finally:
        # Save import statistics regardless of success or failure
        log_entry.airports_created = len(created_iata_list)
        log_entry.airports_updated = len(updated_iata_list)
        log_entry.created_iatas = created_iata_list
        log_entry.updated_iatas = updated_iata_list
        log_entry.end_time = timezone.now()
        log_entry.save()

    return {
        "status": log_entry.status,
        "created": log_entry.airports_created,
        "updated": log_entry.airports_updated,
        "created_iatas": created_iata_list,
        "updated_iatas": updated_iata_list,
        "details": log_entry.details
    }


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the distance between two points in km using the Haversine formula."""
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = EARTH_RADIUS_KM * c
    return distance

def calculate_price(fare: float) -> Dict[str, float]:
    # Fee is 10% of fare with a minimum of R$40
    fee = max(fare * 0.10, 40.0)
    total = fare + fee
    return {
        "fare": round(fare, 2),
        "fee": round(fee, 2),
        "total": round(total, 2)
    }

def calculate_meta(flight: Dict[str, Any], distance: float) -> Dict[str, Any]:
    if distance == 0:
        return {"range": 0, "cruise_speed_kmh": 0, "cost_per_km": 0.0}

    departure_time = datetime.datetime.fromisoformat(flight['departure_time'])
    arrival_time = datetime.datetime.fromisoformat(flight['arrival_time'])
    duration = arrival_time - departure_time
    duration_in_hours = duration.total_seconds() / 3600

    # Calculate average speed during flight
    cruise_speed_kmh = distance / duration_in_hours if duration_in_hours > 0 else 0
    cost_per_km = flight['price']['fare'] / distance if distance > 0 else 0

    return {
        "range": round(distance),
        "cruise_speed_kmh": round(cruise_speed_kmh),
        "cost_per_km": round(cost_per_km, 2)
    }

def fetch_flights_from_api(departure_airport: str, arrival_airport: str, date: str) -> Dict[str, Any]:
    url = f"{MOCK_API_BASE_URL}/{MOCK_API_KEY}/{departure_airport}/{arrival_airport}/{date}"
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(MOCK_API_USER, MOCK_API_PASSWORD),
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_warning('core.services', f"Error fetching data from Mock Airlines API: {str(e)}", {'url': url, 'error': str(e)})
        raise ConnectionError(f"Error fetching data from Mock Airlines API: {e}") from e

def process_flight_options(api_response: Dict[str, Any], distance: float) -> List[Dict[str, Any]]:
    processed_flights = []
    for flight in api_response.get("options", []):
        raw_fare = flight.get("price", {}).get("fare", 0.0)
        # Recalculate price with fees and add flight metadata
        flight["price"] = calculate_price(raw_fare)
        flight["meta"] = calculate_meta(flight, distance)
        processed_flights.append(flight)
    return processed_flights

def find_flight_combinations(
    origin_iata: str,
    destination_iata: str,
    departure_date_str: str,
    return_date_str: str
) -> Dict[str, Any]:

    if not all([origin_iata, destination_iata, departure_date_str, return_date_str]):
        raise ValueError("Missing required search parameters.")
    if origin_iata.upper() == destination_iata.upper():
        raise ValueError("Origin and destination airports cannot be the same.")

    try:
        departure_date = datetime.date.fromisoformat(departure_date_str)
        return_date = datetime.date.fromisoformat(return_date_str)
    except (ValueError, TypeError):
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

    if departure_date < datetime.date.today():
        raise ValueError("Departure date cannot be in the past.")
    if return_date < departure_date:
        raise ValueError("Return date cannot be before the departure date.")

    try:
        origin_airport = Airport.objects.get(iata__iexact=origin_iata)
        destination_airport = Airport.objects.get(iata__iexact=destination_iata)
    except Airport.DoesNotExist:
        log_warning(
            'core.services',
            f"Airport lookup failed for origin={origin_iata} destination={destination_iata}",
            {'origin': origin_iata, 'destination': destination_iata}
        )
        raise ValueError("One or both airports could not be found in our database.")

    distance_km = calculate_distance(
        origin_airport.lat, origin_airport.lon,
        destination_airport.lat, destination_airport.lon
    )

    outbound_api_data = fetch_flights_from_api(origin_iata, destination_iata, departure_date_str)
    outbound_flights = process_flight_options(outbound_api_data, distance_km)
    print(outbound_flights)

    inbound_api_data = fetch_flights_from_api(destination_iata, origin_iata, return_date_str)
    inbound_flights = process_flight_options(inbound_api_data, distance_km)
    print(inbound_flights)

    flight_combinations = []
    for outbound_flight in outbound_flights:
        for inbound_flight in inbound_flights:
            total_price = outbound_flight['price']['total'] + inbound_flight['price']['total']
            combination = {
                "outbound_flight": outbound_flight,
                "inbound_flight": inbound_flight,
                "price": {
                    "total": round(total_price, 2),
                    "currency": outbound_api_data.get("summary", {}).get("currency", "BRL")
                }
            }
            flight_combinations.append(combination)
    # Sort combinations by total price (lambda sorts lower price first by the use of magic), get is used to avoid KeyError in lambda function
    flight_combinations.sort(key=lambda x: x.get('price', {}).get('total', float('inf')))
    return {
        "summary": {
            "from": origin_iata.upper(),
            "to": destination_iata.upper(),
            "departure_date": departure_date_str,
            "return_date": return_date_str,
            "total_outbound_options": len(outbound_flights),
            "total_inbound_options": len(inbound_flights),
            "total_combinations": len(flight_combinations),
        },
        "outbound_options": outbound_flights,
        "inbound_options": inbound_flights,
        "combinations": flight_combinations
    }