from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import logout


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if last activity time is set in session
            if 'last_activity_time' in request.session:
                # Calculate the time elapsed since the last activity
                elapsed_time = datetime.now() - request.session['last_activity_time']
                # If elapsed time is greater than 1 minute, log out the user
                if elapsed_time > timedelta(minutes=1):
                    logout(request)
            # Update the last activity time in session
            request.session['last_activity_time'] = datetime.now()
        response = self.get_response(request)
        return response
