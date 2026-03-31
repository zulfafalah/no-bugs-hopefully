import jwt as pyjwt
from django.conf import settings as django_settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SimpleUser:
    def __init__(self, user_id=1, username='admin'):
        self.id = user_id
        self.pk = user_id
        self.username = username
        self.is_authenticated = True
        self.is_active = True


class CustomJWTAuthentication(BaseAuthentication):
    """JWT authentication that works without a database user."""
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(' ')
            if prefix != 'Bearer':
                return None
        except ValueError:
            return None

        try:
            payload = pyjwt.decode(token, django_settings.SECRET_KEY, algorithms=['HS256'])
            if payload.get('token_type') != 'access':
                raise AuthenticationFailed('Invalid token type')
            user = SimpleUser(payload.get('user_id'), payload.get('username'))
            return (user, token)
        except pyjwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except pyjwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
