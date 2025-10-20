from django.urls import path
from core.views.flights_search_views import FlightSearchView


urlpatterns = [
    path('search/', FlightSearchView.as_view(), name='flight-search'),
]