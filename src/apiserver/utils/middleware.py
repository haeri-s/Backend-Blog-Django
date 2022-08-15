from django.utils.deprecation import MiddlewareMixin
import json

from apiserver.settings.base import JWT_AUTH

# Token Refresh 할 때
# header cookies 에만 token 정보가 있을 경우
# body 에 token 정보 넣어서 전달해줌
class TokenRefreshFromHeaderIntoTheBody(MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        jwt_name = JWT_AUTH.get('JWT_AUTH_COOKIE', 'token')
        if request.path in ['/api/v1/account/refresh-token', '/api/v1/account/verify-token'] and jwt_name in request.COOKIES:
            try:
                data = json.loads(request.body)
            except:
                data = {}
            data['token'] = request.COOKIES[jwt_name]
            request._body = json.dumps(data).encode('utf-8')
        return None