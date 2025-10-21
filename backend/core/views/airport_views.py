from dotenv import load_dotenv

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models.airport_model import Airport
from core.services import import_airports_from_api
from core.utils.logging_utils import log_info, log_error


load_dotenv()


class AirportDetailView(View):
    def get(self, request, *args, **kwargs):
        iata = kwargs.get('iata')
        airport = get_object_or_404(Airport, iata=iata)
        data = {
            'iata': airport.iata,
            'city': airport.city,
            'state': airport.state,
            'lat': airport.lat,
            'lon': airport.lon,
        }
        return JsonResponse(data)

# The outside api handles authentication via POST parameters, so we exempt CSRF for this view specifically
@method_decorator(csrf_exempt, name='dispatch')
class AirportImportView(View):
    def post(self, request, *args, **kwargs):
        user = request.POST.get("user")
        password = request.POST.get("password")
        try:
            result = import_airports_from_api(user=user, password=password)
            log_info('core.views.airport_views', f'Airport import triggered by user={user or "N/A"} result={result.get("status")}')
            return JsonResponse(result)
        except Exception as e:
            log_error('core.views.airport_views', f'Airport import failed: {str(e)}', {'error': str(e)})
            return HttpResponseBadRequest(str(e))


class AirportListView(View):
    def get(self, request, *args, **kwargs):
        airports = Airport.objects.all()
        data = [
            {
                'iata': airport.iata,
                'city': airport.city,
                'state': airport.state,
                'lat': airport.lat,
                'lon': airport.lon,
            }
            for airport in airports
        ]
        return JsonResponse(data, safe=False)