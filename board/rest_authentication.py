from datetime import timedelta
from django.conf import settings
from django.contrib.sessions.models import Session
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone


class ExpiringTokenAuthentication(TokenAuthentication):
    session_time_list = [timezone.now()]

    def authenticate_credentials(self, key):
        user, tok = super().authenticate_credentials(key)
        if user and not user.is_superuser:
            session = Session.objects.order_by('-expire_date').first()
            session_time = session.expire_date
            self.session_time_list.append(session_time)
            model = self.get_model()
            try:
                token = model.objects.select_related('user').get(key=key)
            except model.DoesNotExist:
                return None

            if not token.user.is_active:
                return None

            token_created_time = token.created.time()
            last_session_time = self.session_time_list[-2].time()
            delta_time = (timezone.now() - timedelta(minutes=settings.TOKEN_EXPIRY_TIME)).time()
            if token_created_time < last_session_time < delta_time:
                token.delete()
                return None
        else:
            model = self.get_model()
            try:
                token = model.objects.select_related('user').get(key=key)
            except model.DoesNotExist:
                return None
        return token.user, token
