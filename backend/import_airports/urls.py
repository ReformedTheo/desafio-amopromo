"""
URL configuration for import_airports project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [ 
    path('admin/', admin.site.urls),
    path('api/', include('core.routes.airport_routes')),
    path('api/', include('core.routes.import_log_routes')),
    path('api/', include('core.routes.log_routes')),
    path('api/flights_integration/', include('core.routes.flight_search_routes')),
    path('api/logs/', include('core.routes.log_routes')),
]