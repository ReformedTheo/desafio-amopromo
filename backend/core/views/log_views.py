from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
import os
from datetime import datetime, timedelta

from core.models.log_model import ApplicationLog


API_AUTH_TOKEN = os.getenv("MOCK_API_KEY")


class LogsView(View):
    def get(self, request, *args, **kwargs):
        
        auth_header = request.headers.get('Authorization')
        expected_header = f"Token {API_AUTH_TOKEN}"
        
        if not auth_header or auth_header != expected_header:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        
        logs = ApplicationLog.objects.all()
        
        
        level = request.GET.get('level')
        if level:
            level_upper = level.upper()
            if level_upper in [choice[0] for choice in ApplicationLog.LogLevel.choices]:
                logs = logs.filter(level=level_upper)
            else:
                return JsonResponse({
                    'error': f'Invalid log level. Valid options: {", ".join([choice[0] for choice in ApplicationLog.LogLevel.choices])}'
                }, status=400)
        
        
        date_str = request.GET.get('date')
        date_from_str = request.GET.get('date_from')
        date_to_str = request.GET.get('date_to')
        
        try:
            if date_str:
                
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                logs = logs.filter(
                    timestamp__date=target_date
                )
            else:
               
                if date_from_str:
                    date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
                    logs = logs.filter(timestamp__gte=date_from)
                
                if date_to_str:
                    date_to = datetime.strptime(date_to_str, '%Y-%m-%d')
                    
                    date_to = date_to + timedelta(days=1)
                    logs = logs.filter(timestamp__lt=date_to)
        
        except ValueError as e:
            return JsonResponse({
                'error': 'Invalid date format. Use YYYY-MM-DD format.'
            }, status=400)
        
        page = request.GET.get('page', 1)
        page_size = min(int(request.GET.get('page_size', 50)), 200)
        
        try:
            page = int(page)
        except ValueError:
            return JsonResponse({'error': 'Invalid page number'}, status=400)
        
        paginator = Paginator(logs, page_size)
        
        if page > paginator.num_pages and paginator.num_pages > 0:
            return JsonResponse({'error': f'Page number out of range. Total pages: {paginator.num_pages}'}, status=400)
        
        page_obj = paginator.get_page(page)
        
        
        logs_data = [
            {
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'level': log.level,
                'module': log.module,
                'message': log.message,
                'extra_data': log.extra_data,
            }
            for log in page_obj
        ]
        
        response_data = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'results': logs_data,
        }
        
        return JsonResponse(response_data, status=200, json_dumps_params={'indent': 2})
