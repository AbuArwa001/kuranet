from django.utils.deprecation import MiddlewareMixin

class DisableCSRFCheckMiddleware(MiddlewareMixin):
    """
    Middleware to disable CSRF checks for specific views.
    This is useful for APIs or views that do not require CSRF protection.
    """
    def process_request(self, request):
        # Disable CSRF check for this request
        setattr(request, '_dont_enforce_csrf_checks', True)
        return None