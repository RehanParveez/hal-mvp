from django.conf import settings
from django.http import HttpResponseForbidden

class AdminIPAllowlistMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    if request.path.startswith(f'/{settings.ADMIN_URL_PATH}') and settings.ADMIN_IP_ALLOWLIST:
      client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
      if client_ip not in settings.ADMIN_IP_ALLOWLIST:
        return HttpResponseForbidden("Admin access is restricted.")
    return self.get_response(request)