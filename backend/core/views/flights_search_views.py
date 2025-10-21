from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import os

from core.services import find_flight_combinations
from core.utils.logging_utils import log_info, log_debug, log_warning, log_error


API_AUTH_TOKEN = os.getenv("MOCK_API_KEY")


# The outside api handles authentication via POST parameters, so we exempt CSRF for this view specifically
@method_decorator(csrf_exempt, name='dispatch')
class FlightSearchView(View):
    def get(self, request, *args, **kwargs):

        auth_header = request.headers.get('Authorization')
        expected_header = f"Token {API_AUTH_TOKEN}"

        if not auth_header or auth_header != expected_header:
            log_info('core.views.flights_search_views', f'Unauthorized access attempt to flight search from {request.META.get("REMOTE_ADDR")}')
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        origin = request.GET.get('from')
        destination = request.GET.get('to')
        departure_date = request.GET.get('departureDate')
        return_date = request.GET.get('returnDate')
        
        try:
            flight_data = find_flight_combinations(
                origin_iata=origin,
                destination_iata=destination,
                departure_date_str=departure_date,
                return_date_str=return_date
            )
            return JsonResponse(flight_data, status=200, json_dumps_params={'indent': 2})

        except ValueError as e:
            log_debug('core.views.flights_search_views', f'Validation error in flight search: {str(e)}')
            return JsonResponse({'error': str(e)}, status=400)
        except ConnectionError as e:
            log_warning('core.views.flights_search_views', f'External API error when searching flights: {str(e)}', {'error': str(e)})
            return JsonResponse({'error': f'External API Error: {str(e)}'}, status=503)
        except Exception as e:
            log_error('core.views.flights_search_views', f'Unhandled exception in FlightSearchView: {str(e)}', {'error': str(e)})
            return JsonResponse({'error': 'An unexpected internal server error occurred.'}, status=500)