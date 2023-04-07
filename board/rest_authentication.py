from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            return None

        if not token.user.is_active:
            return None

        # Check token expiry time
        if token.created < timezone.now() - timedelta(minutes=settings.TOKEN_EXPIRY_TIME):
            token.delete()
            return None

        return token.user, token
