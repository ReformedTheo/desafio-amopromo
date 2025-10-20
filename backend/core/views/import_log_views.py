from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from core.models.import_log_model import ImportLogModel


class ImportLogListView(View):
    def get(self, request, *args, **kwargs):
        imports = ImportLogModel.objects.all()
        data = [
            {
                'id': imp.id,
                'start_time': imp.start_time,
                'end_time': imp.end_time,
                'status': imp.status,
                'airports_created': imp.airports_created,
                'airports_updated': imp.airports_updated,
                'created_iatas': imp.created_iatas,
                'updated_iatas': imp.updated_iatas,
                'details': imp.details,
            }
            for imp in imports
        ]
        return JsonResponse(data, safe=False)

class ImportLogDetailView(View):
    def get(self, request, *args, **kwargs):
        import_id = kwargs.get('id')
        import_instance = get_object_or_404(ImportLogModel, id=import_id)
        data = {
            'id': import_instance.id,
            'start_time': import_instance.start_time,
            'end_time': import_instance.end_time,
            'status': import_instance.status,
            'airports_created': import_instance.airports_created,
            'airports_updated': import_instance.airports_updated,
            'created_iatas': import_instance.created_iatas,
            'updated_iatas': import_instance.updated_iatas,
            'details': import_instance.details,
        }
        return JsonResponse(data)