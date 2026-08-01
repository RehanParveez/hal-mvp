import logging
import time

logger = logging.getLogger('hal.audit')
AUDIT_EXEMPT_PREFIXES = ('/admin/', '/static/', '/media/')

class AuditLogMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    if request.path.startswith(AUDIT_EXEMPT_PREFIXES):
      return self.get_response(request)
    start = time.monotonic()
    response = self.get_response(request)
    duration_ms = round((time.monotonic() - start) * 1000, 1)
    user = getattr(request, 'user', None)
    logger.info(
      'request_id=%s user_id=%s role=%s method=%s path=%s status=%s duration_ms=%s',
      getattr(request, 'request_id', '-'),
      str(user.id) if user and user.is_authenticated else '-',
      getattr(user, 'role', '-') if user and user.is_authenticated else '-',
      request.method, request.path, response.status_code, duration_ms,
    )
    return response