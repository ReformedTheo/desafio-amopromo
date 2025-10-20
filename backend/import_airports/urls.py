"""
URL configuration for import_airports project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # URLs do Admin
    path('admin/', admin.site.urls),

    # URLs da aplicação core
    path('api/', include('core.routes.airport_routes')),
    path('api/', include('core.routes.import_log_routes')),
    path('api/flights_integration/', include('core.routes.flight_search_routes'))
]