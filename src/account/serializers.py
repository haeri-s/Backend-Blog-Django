import datetime, re
from calendar import timegm
from django.contrib.auth import authenticate, password_validation
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import VerificationBaseSerializer
from account.models import User, UserAuthentication
from apiserver.utils.jwt import get_jwt_with_login, refresh_jwt_with_login



class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone_number','is_staff', 'provider','last_login', 'is_active')


def jwt_response_payload_handler(token, user=None, request=None):
    # print('tokentokentoken', token)
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    provider = serializers.CharField(max_length=8)
    name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=255)

    def validate(self, attrs):
        try:
            tf = password_validation.validate_password(attrs['password'])
            pw_rex = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}')
            if not re.match(pw_rex, attrs['password']):
                raise Exception()
        except Exception as err:
            raise ValidationError({'detail': {'password': '비밀번호 형식이 맞지 않습니다.'}})
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user


class SnsUserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    provider = serializers.CharField(max_length=8)
    name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=255, allow_null=True)
    
    def create(self, validated_data):
        user = User.objects.create_social(**validated_data)
        return user


class UserPWResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    code = serializers.CharField(max_length=6, allow_null=True)

    def validate(self, data):
        email = data.get("email", None)
        code = data.get("code", None)
        password = data.get("password", None)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError({'detail':{ 'account': '회원정보가 맞지 않습니다.'}})

        if not user.provider == 'email':
            raise ValidationError({'detail': {'provider': '이메일로 가입한 회원이 아닙니다.'}})

        # 탈퇴한 사용자
        if not user.is_active:
            raise AuthenticationFailed(detail='이미 탈퇴한 회원입니다.', code='is_not_active_account')
            
        if code:
            try:
                verify = UserAuthentication.objects.get(email=email, code=code, is_used= False, authentication_type="password")
                if datetime.datetime.now() > verify.expired_at:
                    raise AuthenticationFailed(detail='인증코드가 만료되었습니다.', code='verf_code_has_expired')
                    
                else:
                    verify.is_used = True
                    verify.save()
            except UserAuthentication.DoesNotExist:
                raise AuthenticationFailed(detail='인증코드가 존재하지 않습니다.', code='verf_code_does_not_exists')
        
        try:
            tf = password_validation.validate_password(password)
            pw_rex = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}')
            if not re.match(pw_rex, password):
                raise Exception()
        except Exception as err:
            raise ValidationError({'detail': {'password': '비밀번호 형식이 맞지 않습니다.'}})

        return {
            'email': email, 'code': code, 'password': password
        }

    def update(self, instance, validated_data):
        user = instance
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    
    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        provider = data.get("provider", 'email')
        
        # 회원가입 여부 확인
        try:
            user = User.objects.get(email = email)
        except:
            raise ValidationError({'detail':{ 'account': '회원정보가 맞지 않습니다.'}})

        # provider 확인
        if user.provider != provider:
            raise ValidationError({'detail': {'provider' :f'회원가입 방식이 맞지 않습니다.:{user.get_provider_display()}'}})

        # 비밀번호 확인
        if provider == 'email':
            user = authenticate(username=email, password=password)
            if user is None:
                raise ValidationError({'detail':{ 'account': '회원정보가 맞지 않습니다.'}})

        # 탈퇴한 사용자
        if not user.is_active:
            raise AuthenticationFailed(detail='이미 탈퇴한 회원입니다.', code='is_not_active_account')

        try:
            jwt_token = get_jwt_with_login(user)
        except User.DoesNotExist:
            raise ValidationError({'detail':{ 'account': '회원정보가 맞지 않습니다.'}})

        return {
            'email': user.email,
            'token': jwt_token
        }


class UserRefreshTokenSerializer(VerificationBaseSerializer):
    """
    Refresh an access token.
    """
    token = serializers.CharField()
    email = serializers.EmailField(max_length=255, read_only=True)
    name = serializers.CharField(max_length = 100, read_only=True)


    def validate(self, attrs):
        token = attrs['token']
        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)

        orig_iat = payload.get('orig_iat')
        if orig_iat:
            refresh_limit = api_settings.JWT_REFRESH_EXPIRATION_DELTA

            if isinstance(refresh_limit, datetime.timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 + refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                raise AuthenticationFailed(detail='jwt 토큰이 만료되었습니다.', code='jwt_token_has_expired')
        else:
            raise AuthenticationFailed(detail='jwt token을 재발급하기 위해서는 orig iat 정보가 필요합니다.', code='invalid_refresh_token')

        token = refresh_jwt_with_login(user, orig_iat)

        return {
            'token': token,
            'email': payload['email'],
            'name': payload.get('name', '')
        }
