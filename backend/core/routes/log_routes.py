from django.urls import path
from core.views.log_views import LogsView

urlpatterns = [
    path('', LogsView.as_view(), name='logs-list'),
]
