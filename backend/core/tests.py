import requests
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse

from .models.airport_model import Airport
from .models.import_log_model import ImportLogModel
from .services import import_airports_from_api


class ModelTests(TestCase):

    def test_models_work(self):
        print("[ModelTests] Starting test_models_work")
        airport = Airport.objects.create(
            iata='LHR', city='London', state='ENG', lat=51.47, lon=-0.45
        )
        self.assertEqual(str(airport), "London (LHR)")

        log = ImportLogModel.objects.create(status=ImportLogModel.Status.SUCCESS)
        self.assertIn("Import run on", str(log))
        self.assertIn("SUCCESS", str(log))
        print("[ModelTests] test_models_work completed successfully")


class ImportServiceTest(TestCase):

    def setUp(self):
        Airport.objects.create(iata='JFK', city='New York Old', state='NY', lat=0, lon=0)

    @patch('core.services.requests.get')
    def test_import_success(self, mock_requests_get):
        print("[ImportServiceTest] Starting test_import_success")
        mock_api_data = {
            "LAX": {"iata": "LAX", "city": "Los Angeles", "state": "CA", "lat": 33.94, "lon": -118.40},
            "JFK": {"iata": "JFK", "city": "New York New", "state": "NY", "lat": 40.64, "lon": -73.77},
        }
        mock_requests_get.return_value.json.return_value = mock_api_data
        mock_requests_get.return_value.raise_for_status.return_value = None 

        import_airports_from_api()

        self.assertEqual(Airport.objects.count(), 2)
        print(f"[ImportServiceTest] Airport count after import: {Airport.objects.count()}")
        jfk_updated = Airport.objects.get(iata='JFK')
        self.assertEqual(jfk_updated.city, "New York New")

        log = ImportLogModel.objects.first()
        self.assertEqual(log.status, ImportLogModel.Status.SUCCESS)
        self.assertEqual(log.airports_created, 1)
        self.assertEqual(log.airports_updated, 1)
        print("[ImportServiceTest] test_import_success completed successfully")

    @patch('core.services.requests.get')
    def test_import_api_failure(self, mock_requests_get):
        print("[ImportServiceTest] Starting test_import_api_failure")
        mock_requests_get.side_effect = requests.exceptions.Timeout("API timed out")
        import_airports_from_api()
        self.assertEqual(Airport.objects.count(), 1)
        log = ImportLogModel.objects.first()
        self.assertEqual(log.status, ImportLogModel.Status.FAILED)
        self.assertIn("Failed to fetch data from API", log.details)
        print("[ImportServiceTest] test_import_api_failure completed successfully")


class ViewsTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.airport = Airport.objects.create(
            iata='CDG', city='Paris', state='FR', lat=49.00, lon=2.54
        )
        self.log = ImportLogModel.objects.create(status='SUCCESS')

    def test_list_and_detail_endpoints(self):
        print("[ViewsTest] Starting test_list_and_detail_endpoints")
        list_res = self.client.get(reverse('airport-list'))
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(len(list_res.json()), 1)

        detail_res = self.client.get(reverse('airport-detail', args=['CDG']))
        self.assertEqual(detail_res.status_code, 200)
        self.assertEqual(detail_res.json()['iata'], 'CDG')

        not_found_res = self.client.get(reverse('airport-detail', args=['XXX']))
        self.assertEqual(not_found_res.status_code, 404)
        print("[ViewsTest] test_list_and_detail_endpoints completed successfully")

    @patch('core.views.airport_views.import_airports_from_api')
    def test_import_endpoint(self, mock_import_service):
        print("[ViewsTest] Starting test_import_endpoint")
        mock_import_service.return_value = {"status": "SUCCESS", "created": 1}
        
        response = self.client.post(reverse('airport-import'), data={'user': 'u', 'pass': 'p'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], "SUCCESS")
        mock_import_service.assert_called_once()
        print("[ViewsTest] test_import_endpoint completed successfully")

# flights/tests.py

import datetime
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.urls import reverse

from .services import (
    calculate_distance,
    calculate_price,
    calculate_meta,
    find_flight_combinations,
)
from .views import API_AUTH_TOKEN
from core.models.airport_model import Airport

# --- Mock Data for API Responses ---

MOCK_OUTBOUND_FLIGHTS_API_RESPONSE = {
    "summary": {
        "departure_date": "2025-12-20",
        "from": {"iata": "POA", "city": "Porto Alegre"},
        "to": {"iata": "MAO", "city": "Manaus"},
        "currency": "BRL"
    },
    "options": [
        {
            "departure_time": "2025-12-20T10:00:00",
            "arrival_time": "2025-12-20T14:00:00",
            "price": {"fare": 1200.00},
            "aircraft": {"model": "A320"}
        },
        {
            "departure_time": "2025-12-20T12:00:00",
            "arrival_time": "2025-12-20T16:00:00",
            "price": {"fare": 1350.50},
            "aircraft": {"model": "B737"}
        }
    ]
}

MOCK_INBOUND_FLIGHTS_API_RESPONSE = {
    "summary": {
        "departure_date": "2025-12-25",
        "from": {"iata": "MAO", "city": "Manaus"},
        "to": {"iata": "POA", "city": "Porto Alegre"},
        "currency": "BRL"
    },
    "options": [
        {
            "departure_time": "2025-12-25T15:00:00",
            "arrival_time": "2025-12-25T19:00:00",
            "price": {"fare": 1100.00},
            "aircraft": {"model": "A320"}
        }
    ]
}


class ServicesTests(TestCase):
    """Tests for the business logic in services.py."""

    def test_calculate_distance(self):
        """Test distance calculation between POA and MAO."""
        poa = Airport.objects.get(iata="POA")
        mao = Airport.objects.get(iata="MAO")
        distance = calculate_distance(poa.lat, poa.lon, mao.lat, mao.lon)
        # Approximate distance is ~3130 km
        self.assertGreater(distance, 3100)
        self.assertLess(distance, 3200)

    def test_calculate_price(self):
        """Test fee and total price calculation."""
        # Case 1: 10% of fare is greater than 40.0
        price1 = calculate_price(500.00)
        self.assertEqual(price1, {"fare": 500.00, "fee": 50.00, "total": 550.00})

        # Case 2: 10% of fare is less than 40.0
        price2 = calculate_price(300.00)
        self.assertEqual(price2, {"fare": 300.00, "fee": 40.00, "total": 340.00})

    def test_calculate_meta(self):
        """Test flight metadata calculation."""
        mock_flight = {
            "departure_time": "2025-12-20T10:00:00",
            "arrival_time": "2025-12-20T14:00:00", # 4 hour duration
            "price": {"fare": 1200.00}
        }
        distance = 3130.0  # km
        meta = calculate_meta(mock_flight, distance)

        self.assertEqual(meta["range"], 3130)
        self.assertEqual(meta["cruise_speed_kmh"], 783) # 3130 km / 4 hours
        self.assertAlmostEqual(meta["cost_per_km"], 0.38, places=2)

    @patch('flights.services._fetch_flights_from_api')
    def test_find_flight_combinations_success(self, mock_fetch):
        """Test the main service function on a successful run."""
        # Configure the mock to return different data for each call
        mock_fetch.side_effect = [
            MOCK_OUTBOUND_FLIGHTS_API_RESPONSE,
            MOCK_INBOUND_FLIGHTS_API_RESPONSE
        ]

        result = find_flight_combinations("POA", "MAO", "2025-12-20", "2025-12-25")

        self.assertEqual(result['summary']['total_outbound_options'], 2)
        self.assertEqual(result['summary']['total_inbound_options'], 1)
        self.assertEqual(result['summary']['total_combinations'], 2)

        # Verify combinations are sorted by price
        # Combination 1: 1320 (outbound) + 1210 (inbound) = 2530
        # Combination 2: 1485.55 (outbound) + 1210 (inbound) = 2695.55
        self.assertEqual(result['combinations'][0]['price']['total'], 2530.00)
        self.assertEqual(result['combinations'][1]['price']['total'], 2695.55)

        # Check if an outbound option has the enriched data
        first_outbound = result['outbound_options'][0]
        self.assertIn('meta', first_outbound)
        self.assertEqual(first_outbound['price']['total'], 1320.00) # 1200 fare + 120 fee

    def test_find_flight_combinations_validation_errors(self):
        """Test service-level input validations."""
        today = datetime.date.today().isoformat()
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

        # Same origin and destination
        with self.assertRaisesMessage(ValueError, "Origin and destination airports cannot be the same."):
            find_flight_combinations("GRU", "GRU", today, tomorrow)

        # Non-existent airport
        with self.assertRaisesMessage(ValueError, "One or both airports could not be found"):
            find_flight_combinations("XXX", "GRU", today, tomorrow)

        # Past departure date
        with self.assertRaisesMessage(ValueError, "Departure date cannot be in the past."):
            find_flight_combinations("GRU", "POA", "2020-01-01", today)

        # Return date before departure
        with self.assertRaisesMessage(ValueError, "Return date cannot be before the departure date."):
            find_flight_combinations("GRU", "POA", tomorrow, today)


class FlightSearchViewTests(TestCase):
    """Tests for the API endpoint in views.py."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('flights:flight-search')
        self.valid_params = {
            'from': 'POA',
            'to': 'MAO',
            'departureDate': '2025-12-20',
            'returnDate': '2025-12-25',
        }
        self.auth_header = {'HTTP_AUTHORIZATION': f'Token {API_AUTH_TOKEN}'}

    def test_authentication_failure(self):
        """Test that requests without or with invalid token are rejected."""
        # No token
        response = self.client.get(self.url, self.valid_params)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'error': 'Unauthorized'})

        # Invalid token
        response = self.client.get(self.url, self.valid_params, HTTP_AUTHORIZATION='Token invalid-token')
        self.assertEqual(response.status_code, 401)

    def test_missing_parameters(self):
        """Test for 400 Bad Request if a parameter is missing."""
        invalid_params = self.valid_params.copy()
        del invalid_params['to']
        response = self.client.get(self.url, invalid_params, **self.auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required search parameters', response.json()['error'])

    @patch('flights.views.find_flight_combinations')
    def test_validation_error_from_service(self, mock_find):
        """Test that view returns 400 on ValueError from service."""
        mock_find.side_effect = ValueError("Test validation error.")
        response = self.client.get(self.url, self.valid_params, **self.auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Test validation error.'})

    @patch('flights.views.find_flight_combinations')
    def test_external_api_connection_error(self, mock_find):
        """Test that view returns 503 on ConnectionError from service."""
        mock_find.side_effect = ConnectionError("Failed to connect.")
        response = self.client.get(self.url, self.valid_params, **self.auth_header)
        self.assertEqual(response.status_code, 503)
        self.assertIn('External API Error', response.json()['error'])

    @patch('flights.views.find_flight_combinations')
    def test_successful_request(self, mock_find):
        """Test a full, successful 200 OK request."""
        mock_response_data = {"summary": "Success", "combinations": []}
        mock_find.return_value = mock_response_data

        response = self.client.get(self.url, self.valid_params, **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_response_data)

        # Ensure the service was called with the correct parameters
        mock_find.assert_called_once_with(
            origin_iata='POA',
            destination_iata='MAO',
            departure_date_str='2025-12-20',
            return_date_str='2025-12-25'
        )