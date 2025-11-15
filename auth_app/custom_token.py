from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.dateparse import parse_datetime

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        token_pwd_change = parse_datetime(validated_token.get('last_password_change'))
        if token_pwd_change and user.last_password_change > token_pwd_change:
            raise AuthenticationFailed('Password has been changed. Please log in again.')
        return user
