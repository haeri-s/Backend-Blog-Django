"""
    JWT 설정
"""
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import update_last_login

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

def get_jwt_with_login(user, orig_iat = None):
    payload = JWT_PAYLOAD_HANDLER(user)
    if orig_iat:
        payload['orig_iat'] = orig_iat
    jwt_token = JWT_ENCODE_HANDLER(payload)
    update_last_login(None, user)
    return jwt_token

def refresh_jwt_with_login(user, orig_iat):
    token = get_jwt_with_login(user, orig_iat)
    return token
    