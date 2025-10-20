from django.urls import path
from core.views.airport_views import AirportImportView, AirportDetailView, AirportListView

urlpatterns = [
    path('airports/import/', AirportImportView.as_view(), name='airport-import'),
    path('airports/', AirportListView.as_view(), name='airport-list'),
    path('airports/<str:iata>/', AirportDetailView.as_view(), name='airport-detail'),
]
