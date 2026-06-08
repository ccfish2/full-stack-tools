from django.http import JsonResponse


def api_hello(request):
    return JsonResponse({
        "message": "Hello from Django backend",
        "status": "ok",
    })
