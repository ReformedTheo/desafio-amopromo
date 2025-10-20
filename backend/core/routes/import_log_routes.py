from django.urls import path
from core.views.import_log_views import ImportLogListView, ImportLogDetailView


urlpatterns = [
    path('import-logs/', ImportLogListView.as_view(), name='import-log-list'),
    path('import-logs/<int:id>/', ImportLogDetailView.as_view(), name='import-log-detail'),
]