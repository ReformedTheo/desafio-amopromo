from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from core.services import find_flight_combinations


API_AUTH_TOKEN = "a-very-secure-and-hard-to-guess-token"


# The outside api handles authentication via POST parameters, so we exempt CSRF for this view specifically
@method_decorator(csrf_exempt, name='dispatch')
class FlightSearchView(View):
    def get(self, request, *args, **kwargs):

        auth_header = request.headers.get('Authorization')
        expected_header = f"Token {API_AUTH_TOKEN}"

        if not auth_header or auth_header != expected_header:
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
            return JsonResponse({'error': str(e)}, status=400)
        except ConnectionError as e:
            return JsonResponse({'error': f'External API Error: {str(e)}'}, status=503)
        except Exception:
            return JsonResponse({'error': 'An unexpected internal server error occurred.'}, status=500)