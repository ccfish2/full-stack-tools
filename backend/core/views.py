from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import StatsigApplication


def api_hello(request):
    return JsonResponse({
        "message": "Hello from Django backend",
        "status": "ok",
    })


@csrf_exempt
@require_http_methods(["POST"])
def statsig_application(request):
    """
    POST /statsig/application
    Accepts JSON data and persists it to the database
    """
    try:
        # Parse the JSON body
        data = json.loads(request.body)
        
        # Create a new StatsigApplication record
        app_record = StatsigApplication.objects.create(data=data)
        
        return JsonResponse({
            "status": "success",
            "id": app_record.id,
            "data": app_record.data,
            "created_at": app_record.created_at.isoformat(),
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
