from django.contrib.auth import logout


class BanMiddleware:
    """Log out users that were banned during an active session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_banned:
            logout(request)
        return self.get_response(request)
