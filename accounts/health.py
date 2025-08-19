from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Backend is running',
        'available_endpoints': [
            '/api/accounts/register/',
            '/api/accounts/login/',
            '/api/accounts/profile/',
        ]
    })
