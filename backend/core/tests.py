import datetime
from unittest.mock import patch
import requests
from django.test import TestCase, Client
from django.urls import reverse
from .models.airport_model import Airport
from .models.import_log_model import ImportLogModel
from .services import (
    import_airports_from_api,
    calculate_distance,
    calculate_price,
    calculate_meta,
    find_flight_combinations,
)
from core.views.flights_search_views import API_AUTH_TOKEN


class ModelAndImportTests(TestCase):
    """
    - Ensure basic model string representations work.
    - Test import service success and a simulated API failure.

    Expected:
    - On successful import (mocked API returns data), new airports are created/updated and
      ImportLogModel records SUCCESS with counts.
    - On API failure (requests exception), the service still writes a FAILED ImportLog entry
      and does not create new airports.
    """

    def test_models_and_import(self):
        print("[ModelAndImportTests] start")

        a = Airport.objects.create(iata='TEST', city='Test City', state='TS', lat=1.0, lon=2.0)
        self.assertIn('Test City', str(a))


        Airport.objects.create(iata='JFK', city='Old', state='ST', lat=0.0, lon=0.0)


        with patch('core.services.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'JFK': {'iata': 'JFK', 'city': 'New City', 'state': 'ST', 'lat': 1.0, 'lon': 1.0},
                'LAX': {'iata': 'LAX', 'city': 'LA', 'state': 'CA', 'lat': 34.0, 'lon': -118.0},
            }
            mock_get.return_value.raise_for_status.return_value = None

            result = import_airports_from_api()


            self.assertEqual(result['status'], ImportLogModel.Status.SUCCESS)
            self.assertEqual(result['created'], 1)  # LAX created
            self.assertEqual(result['updated'], 1)  # JFK updated


        with patch('core.services.requests.get') as mock_get2:
            mock_get2.side_effect = requests.exceptions.Timeout('timeout')
            result2 = import_airports_from_api()
            self.assertEqual(result2['status'], ImportLogModel.Status.FAILED)
        print("[ModelAndImportTests] end")


class ServiceHelpersTests(TestCase):
    """
    Tests for helper functions: distance, price calculation, and meta calculation.

    Expected:
    - calculate_distance returns value in km between two coordinates.
    - calculate_price applies a 10% fee with a minimum of 40.
    - calculate_meta computes range, cruise speed, and cost/km from flight data.
    """

    def setUp(self):
        Airport.objects.update_or_create(iata='POA', defaults={'city': 'POA', 'state': 'RS', 'lat': -30.03, 'lon': -51.23})
        Airport.objects.update_or_create(iata='MAO', defaults={'city': 'MAO', 'state': 'AM', 'lat': -3.13, 'lon': -60.02})

    def test_distance_and_price_and_meta(self):
        print("[ServiceHelpersTests] start")
        poa = Airport.objects.get(iata='POA')
        mao = Airport.objects.get(iata='MAO')
        dist = calculate_distance(poa.lat, poa.lon, mao.lat, mao.lon)
        self.assertGreater(dist, 3000)

        p = calculate_price(1000.0)
        self.assertEqual(p['fare'], 1000.0)
        self.assertEqual(p['fee'], 100.0)
        self.assertEqual(p['total'], 1100.0)

        flight = {
            'departure_time': '2025-12-20T10:00:00',
            'arrival_time': '2025-12-20T14:00:00',
            'price': {'fare': 1200.0}
        }
        meta = calculate_meta(flight, dist)
        self.assertIn('range', meta)
        self.assertIn('cruise_speed_kmh', meta)
        self.assertIn('cost_per_km', meta)
        print("[ServiceHelpersTests] end")


class FindFlightsServiceTest(TestCase):
    """
    Test the core flight combination service with a mocked external API.

    Expected:
    - When the mocked API returns outbound and inbound options, the service returns
      a payload including 'summary', 'outbound_options', 'inbound_options', and 'combinations'.
    - Validation errors (missing params, invalid dates, airports missing) raise ValueError.
    """

    def setUp(self):
        Airport.objects.update_or_create(iata='POA', defaults={'city': 'POA', 'state': 'RS', 'lat': -30.03, 'lon': -51.23})
        Airport.objects.update_or_create(iata='MAO', defaults={'city': 'MAO', 'state': 'AM', 'lat': -3.13, 'lon': -60.02})

        self.out_resp = {
            'summary': {'currency': 'BRL'},
            'options': [
                {'departure_time': '2025-12-20T10:00:00', 'arrival_time': '2025-12-20T14:00:00', 'price': {'fare': 1200.0}, 'aircraft': {'model': 'A320'}},
                {'departure_time': '2025-12-20T12:00:00', 'arrival_time': '2025-12-20T16:00:00', 'price': {'fare': 1350.5}, 'aircraft': {'model': 'B737'}},
            ]
        }
        self.in_resp = {
            'summary': {'currency': 'BRL'},
            'options': [
                {'departure_time': '2025-12-25T15:00:00', 'arrival_time': '2025-12-25T19:00:00', 'price': {'fare': 1100.0}, 'aircraft': {'model': 'A320'}},
            ]
        }

    @patch('core.services.fetch_flights_from_api')
    def test_find_success(self, mock_fetch):
        print("[FindFlightsServiceTest] start")
        mock_fetch.side_effect = [self.out_resp, self.in_resp]
        result = find_flight_combinations('POA', 'MAO', '2025-12-20', '2025-12-25')

        self.assertIn('summary', result)
        self.assertEqual(result['summary']['total_outbound_options'], 2)
        self.assertEqual(result['summary']['total_inbound_options'], 1)
        self.assertEqual(result['summary']['total_combinations'], 2)
        print("[FindFlightsServiceTest] end")

    def test_validation_errors(self):
        # missing params
        with self.assertRaises(ValueError):
            find_flight_combinations('', 'MAO', '2025-12-20', '2025-12-25')

        # same origin/destination
        with self.assertRaises(ValueError):
            find_flight_combinations('POA', 'POA', '2025-12-20', '2025-12-25')

        # invalid date
        with self.assertRaises(ValueError):
            find_flight_combinations('POA', 'MAO', 'bad-date', '2025-12-25')


class FlightSearchViewTests(TestCase):
    """
    A small set of view tests for the FlightSearch endpoint.

    Expected behavior:
    - Unauthorized requests (missing/incorrect token) -> 401
    - Missing parameters -> 400
    - Valid request -> 200 with payload returned from service
    """

    def setUp(self):
        self.client = Client()
        self.url = reverse('flight-search')
        self.valid_params = {
            'from': 'SDU',
            'to': 'GRU',
            'departureDate': datetime.now().date().isoformat(),
            'returnDate': (datetime.now().date() + datetime.timedelta(days=5)).isoformat(),
        }
        self.auth_header = {'HTTP_AUTHORIZATION': f'Token {API_AUTH_TOKEN}'}

    def test_unauthorized(self):
        print("[FlightSearchViewTests] start")
        r = self.client.get(self.url, self.valid_params)
        self.assertEqual(r.status_code, 401)

        r2 = self.client.get(self.url, self.valid_params, HTTP_AUTHORIZATION='Token bad')
        self.assertEqual(r2.status_code, 401)
        print("[FlightSearchViewTests] end")