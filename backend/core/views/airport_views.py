from dotenv import load_dotenv

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models.airport_model import Airport
from core.services import import_airports_from_api


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
            return JsonResponse(result)
        except Exception as e:
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