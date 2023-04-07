from datetime import timedelta


class SessionTimeoutMiddleware:
    """
    Middleware for user logout after expire time

    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                request.session.set_expiry(timedelta(minutes=1))
        response = self.get_response(request)
        return response
