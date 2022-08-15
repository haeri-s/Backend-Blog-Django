from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.contrib.auth import logout as auth_logout
from drf_yasg.utils import  swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny,  IsAuthenticated
from rest_framework_jwt.views import  VerifyJSONWebToken
from account.serializers import UserRegistrationSerializer, SnsUserRegistrationSerializer, UserLoginSerializer, UserSerializer, User, UserAuthentication, UserRefreshTokenSerializer
from apiserver.utils.jwt import get_jwt_with_login
from apiserver.utils.utils import  delete_token_in_cookies, set_token_in_cookies
from apiserver.utils.customApiDocument import ErrorCollection, user_login_schema, status_object_schema
from django.views.decorators.csrf import  ensure_csrf_cookie


@method_decorator(ensure_csrf_cookie, 'dispatch')
class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_id='account_signup',
        operation_summary='이메일 회원가입 API',
        operation_description='이메일 방식으로 회원가입하기',
        responses={
            status.HTTP_201_CREATED: user_login_schema
            , status.HTTP_400_BAD_REQUEST: 
                ErrorCollection('validation_code', status.HTTP_400_BAD_REQUEST,  {'password': '비밀번호 형식이 맞지 않습니다.'}).as_md()
                + ErrorCollection('validation_code', status.HTTP_400_BAD_REQUEST,  {'provider': '회원가입 방식이 맞지 않습니다.:kakao'}).as_md()
            , status.HTTP_401_UNAUTHORIZED:
                ErrorCollection('verf_code_does_not_exists', status.HTTP_401_UNAUTHORIZED, '인증코드가 존재하지 않습니다.').as_md()
        }
    )
    def post(self, request):
        provider = request.data.get("provider", 'email')
        
        email = request.data.get("email", None)
        if provider == 'email':
            email_verify = UserAuthentication.objects.filter(email=email, authentication_type="email", is_used= True).order_by('-updated_at')
            if not email_verify.exists() :
                raise AuthenticationFailed(detail='인증코드가 존재하지 않습니다.', code='verf_code_does_not_exists')
            if datetime.now() > (email_verify[0].updated_at + timedelta(hours=1)): # 인증 후 1시간
                raise AuthenticationFailed(detail='인증코드가 만료되었습니다.', code='verf_code_has_expired') #
            serializer = self.serializer_class(data=request.data)
        else:
            raise ValidationError({'provider': f'회원가입 방식이 맞지 않습니다.:{provider}'})

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.details.save()

        jwt_token = get_jwt_with_login(user)
        user = UserSerializer(user)

        response = {
            'status' : 'success',
            'result': {
                'token': jwt_token,
                'user': user.data
            },
        }
        res = Response(response, status=status.HTTP_201_CREATED)
        res = set_token_in_cookies(res, jwt_token)

        return res


@method_decorator(ensure_csrf_cookie, 'dispatch')
class UserSNSRegistrationView(CreateAPIView):
    serializer_class = SnsUserRegistrationSerializer
    permission_classes = (AllowAny,)
    def post(self, request):
        provider = request.data.get("provider", 'email')
        
        if provider == 'email':
            raise ValidationError({'provider': f'회원가입 방식이 맞지 않습니다.:{provider}'})
        else:
            serializer = SnsUserRegistrationSerializer(data=request.data)
        
        try:
            user = User.objects.get(email=request.data.get('email'), provider = request.data.get('provider'))
            if not user.is_active:
                raise AuthenticationFailed(detail = '탈퇴한 회원입니다.', code='is_not_active_account')
        except:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

        jwt_token = get_jwt_with_login(user)
        user = UserSerializer(user)

        response = {
            'status' : 'success',
            'result': {
                'token': jwt_token,
                'user': user.data
            },
        }
        res = Response(response, status=status.HTTP_201_CREATED)
        res = set_token_in_cookies(res, jwt_token)
        
        return res

@method_decorator(ensure_csrf_cookie, 'dispatch')
class UserLoginView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        operation_id='account_email_login',
        operation_summary='이메일 로그인 API',
        operation_description='이메일 방식으로 로그인하기',
        responses={
            status.HTTP_201_CREATED: user_login_schema
            , status.HTTP_400_BAD_REQUEST: 
                ErrorCollection('validation_code', status.HTTP_400_BAD_REQUEST,  {'account': '회원정보가 맞지 않습니다.'}).as_md()
                + ErrorCollection('validation_code', status.HTTP_400_BAD_REQUEST,  {'provider': '회원가입 방식이 맞지 않습니다.:kakao'}).as_md()
            , status.HTTP_401_UNAUTHORIZED:
                ErrorCollection('is_not_active_account', status.HTTP_401_UNAUTHORIZED, '이미 탈퇴한 회원입니다.').as_md()
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_serializer = UserSerializer(instance = User.objects.get(email = serializer.data['email']))
        response = {
            'status' : 'success',
            'result' : {
                'token' : serializer.data['token'],
                'user': user_serializer.data
                }
            }

        res = Response(response, status=status.HTTP_201_CREATED)
        res = set_token_in_cookies(res, serializer.data['token'])
        return res

class UserRefreshTokenView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRefreshTokenSerializer

    @swagger_auto_schema(
        operation_id='account_token_refresh',
        operation_summary='인증 토큰 재발행 API',
        operation_description='인증 토큰 재발행하기',
        responses={
            status.HTTP_205_RESET_CONTENT: user_login_schema
            , status.HTTP_401_UNAUTHORIZED:
                ErrorCollection('jwt_token_has_expired', status.HTTP_401_UNAUTHORIZED, 'jwt 토큰이 만료되었습니다.').as_md()
                + ErrorCollection('invalid_refresh_token', status.HTTP_401_UNAUTHORIZED, 'jwt token을 재발급하기 위해서는 orig iat 정보가 필요합니다.').as_md()
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_serializer = UserSerializer(instance = User.objects.get(email = serializer.data['email']))
        response = {
            'status' : 'success',
            'result' : {
                    'token' : serializer.data['token'],
                    'user': user_serializer.data
                }
            }
        res = Response(response, status=status.HTTP_201_CREATED)
        res = set_token_in_cookies(res, serializer.data['token'])
        return res


class UserVerifyTokenView(VerifyJSONWebToken):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='account_token_verify',
        operation_summary='인증 토큰 확인 API',
        operation_description='인증 토큰 확인하기',
        responses={
            status.HTTP_205_RESET_CONTENT: user_login_schema
            , status.HTTP_401_UNAUTHORIZED:
                ErrorCollection('jwt_token_has_expired', status.HTTP_401_UNAUTHORIZED, 'jwt 토큰이 만료되었습니다.').as_md()
                + ErrorCollection('invalid_refresh_token', status.HTTP_401_UNAUTHORIZED, 'jwt token을 재발급하기 위해서는 orig iat 정보가 필요합니다.').as_md()
        }
    )
    def post(self, request):
        res = super().post(request=request)
        token = res.data.get('token', None)
        if not token:
            res = Response({'status': 'error', 'detail': '토큰이 유효하지 않습니다.', 'error_code': 'error_decoding_signature'}, status=status.HTTP_403_FORBIDDEN)
            res = delete_token_in_cookies(res)
        elif type(token) is list:
            res = Response({'status': 'error', 'detail': '토큰 정보가 포함되지 않았습니다.', 'error_code': 'token_not_found'}, status=status.HTTP_401_UNAUTHORIZED)
            res = delete_token_in_cookies(res)

        return res



class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='account_logout',
        operation_summary='회원 로그아웃 API',
        operation_description='회원 로그아웃하기',
        responses={
            status.HTTP_205_RESET_CONTENT : status_object_schema
        }
    )
    def post(self, request):
        response = { 'status' : 'success' }
        auth_logout(request)
        res = Response(response, status=status.HTTP_205_RESET_CONTENT)
        res = delete_token_in_cookies(res)
        return res

