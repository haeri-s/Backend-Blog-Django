# -*- coding: utf-8 -*-
import uuid, re
from django.db import models, IntegrityError
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.core.exceptions import ValidationError as VError

class UserManager(BaseUserManager):
    def create_user(self, email, password, name, phone_number, provider= 'email'):
        if not email:
            raise ValidationError({'detail': {'email': 'EMAIL_IS_REQUIRED'}})

        user = self.model(
            email=self.normalize_email(email),
            provider=provider
        )
        user.name = name
        user.phone_number = phone_number
        if provider == 'email':
            if not password:
                raise ValidationError({'detail': {'password': 'PASSWORD_IS_REQUIRED'}})
            user.set_password(password)
        else:
            # SNS 회원일 경우 비밀번호 사용하지 않는 회원으로 저장
            user.set_unusable_password()
        try:
            user.save(using=self._db)
        except IntegrityError:
            raise AuthenticationFailed(detail = '이미 가입되어 있는 이메일입니다.', code='email_already_exists')
        
        return user

    def create_social(self, email, name, phone_number, provider):
        user = self.create_user(email=email, password=None, name=name, phone_number=phone_number, provider=provider)
        return user

    def create_staff(self, email, password, name=None, phone_number=None):
        if password is None:
            raise TypeError('Super Users must have a password.')
        if name is None:
            name = '직원'
        user = self.create_user(email=email, password=password, name=name, phone_number=phone_number)
        user.is_staff = True
        user.save()

        return user

    def create_superuser(self, email, password, name=None, phone_number=None):
        if password is None:
            raise TypeError('Super Users must have a password.')
        if name is None:
            name = '직원'
        user = self.create_user(email=email, password=password, name=name, phone_number=phone_number)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


# 회원 DB
class User(AbstractBaseUser):
    PROVIDER_CHOICES = [('email', '이메일'), ('kakao', '카카오'), ('naver', '네이버'), ('google', '구글')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name='이메일 주소', max_length=255, unique=True )
    provider = models.CharField(verbose_name='회원가입 방법', max_length=8, default='email', choices=PROVIDER_CHOICES)

    name = models.CharField(verbose_name='회원명', max_length=255, null=False)
    phone_number = models.CharField(verbose_name='휴대폰 번호',max_length=15, default=None, null=True, help_text='숫자만 입력해주세요.', blank=True) 

    is_dormanted = models.BooleanField(default=False, verbose_name="휴면계정여부") 
    is_active = models.BooleanField(default=True, verbose_name="활성계정여부", help_text='탈퇴된 경우 False') 
    deleted_at = models.DateTimeField(verbose_name='회원탈퇴일시', null=True)

    is_staff = models.BooleanField(default=False, verbose_name='직원 여부')
    is_superuser = models.BooleanField(default=False, verbose_name='총괄직원 여부', help_text='결제취소 등의 모든 권한을 가진 직원')
    
    created_at = models.DateTimeField(verbose_name='회원가입일시', auto_now_add=True) 
    updated_at = models.DateTimeField(verbose_name='정보수정일시', auto_now=True) 

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    class Meta:
        db_table = "User"
        verbose_name = '회원'
        verbose_name_plural='회원 관리'

    def __str__(self):
        return self.email

    def get_username(self):
        return self.email 

    def get_full_name(self):   
        return self.name

    def get_short_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff
    
    def clean(self):
        if self.phone_number:
            r = re.compile('[^0-9]')
            tmp = r.findall(self.phone_number)
            if tmp:
                raise VError({'phone_number': '핸드폰 번호는 숫자만 입력 가능합니다.'})


# 회원 인증 DB
class UserAuthentication(models.Model):
    TYPE_CHOICES = [('email', '이메일 인증번호')]
    class Meta:
        db_table = "UserAuthentication"
        verbose_name = '회원 인증'
        verbose_name_plural='회원 인증 관리'

    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name='이메일 주소', max_length=255, unique=False)
    code = models.CharField(verbose_name='인증코드', max_length=6, null=False)
    authentication_type = models.CharField(max_length=9, default = 'email', choices=TYPE_CHOICES)
    expired_at =  models.DateTimeField()
    is_used = models.BooleanField(default = False, verbose_name='코드 사용 여부')

    sended_at = models.DateTimeField(verbose_name='발송일', auto_now_add=True)  # 생성일
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)  # 생성일
    updated_at = models.DateTimeField(verbose_name='정보수정일', auto_now=True)  # 수정일

