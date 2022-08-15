from django.test import TestCase
from account.models import User
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import  reverse
from apiserver.utils.test_data import USER_DATA

BASE_URL = '/api/v1/account/'

class AccountUrlTest(TestCase):
    def test_login_url(self):
        found = resolve('/api/v1/account/login')
        self.assertEqual(found.url_name, 'login')


class AccountTest(APITestCase):
    # 회원가입 테스트
    def test_create_account(self):
        email_data = {
            'email': 'unittest@test.co.kr',
        }

        # 회원가입하기
        url = reverse('account:signup')
        data = {
            'email': 'unittest@test.co.kr', 
            'provider': 'email', 
            'password': 'qweqwe!12',
            'name': '테스트',
            'phone_number': '010012341234'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')


class AccountLoginTest(APITestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for user in USER_DATA:
            User.objects.create_user(**user)

    # 로그인
    def test_email_login(self):
        url = reverse('account:login')
        response = self.client.post(url, USER_DATA[0], format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
    
    # 비밀번호 패턴 오류
    def test_fail_reset_password_without_login(self):
        url = reverse('account:reset_pw')

        res = self.client.post(url, {'email': USER_DATA[1]['email']})
        response = self.client.put(url, {
            'code': res.data['result']['code'],
            'email': res.data['result']['email'],
            'password': 'testpw11'
        })
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AccountWithLoginUser(APITestCase):
    LOGIN_USER = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for user in USER_DATA:
            User.objects.create_user(**user)
    
    def setUp(self):
        url = reverse('account:login')
        login_res = self.client.post(url, USER_DATA[-1], format='json')
        self.LOGIN_USER = login_res.data['result']

    # 토큰 재발행
    def test_refresh_token(self):
        url = reverse('account:refresh-token')
        response = self.client.post(url, {'token': self.LOGIN_USER['token']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('status'), 'success')
        self.assertEqual(self.LOGIN_USER.get('user').get('id'), response.data['result']['user'].get('id'))

    # 로그아웃
    def test_logout(self):
        url = reverse('account:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data['status'], 'success')