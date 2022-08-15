import random
from django.urls import  reverse
from rest_framework.test import APITestCase
from blog.models import Blog
from rest_framework import  status
from apiserver.utils.test_data import BLOG_DATA

TOTAL = 34

class BlogTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        datas = [Blog(**BLOG_DATA, status=['showing', 'bookmark'][random.choice(range(0,2))]) for _ in range(0, TOTAL)]
        Blog.objects.bulk_create(datas)
        return
    
    # 블로그 목록 가져오기
    def test_get_blog_list(self):
        url = reverse('blog:blog_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIsNone(response.data['result']['previous'])
        self.assertIsNotNone(response.data['result']['next'])
        self.assertEqual(response.data['result']['total'], TOTAL)
        self.assertTrue(isinstance(response.data['result']['data'], list))

        response = self.client.get(response.data['result']['next'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIsNotNone(response.data['result']['previous'])
        self.assertIsNotNone(response.data['result']['next'])
        self.assertEqual(response.data['result']['total'], TOTAL)
        self.assertTrue(isinstance(response.data['result']['data'], list))
    
    # 자주찾는 블로그 목록 가져오기
    def test_get_bookmark(self):
        url = reverse('blog:blog_bookmark')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue(len(response.data['result']['data']) <= 3)
        self.assertTrue(isinstance(response.data['result']['data'], list))


    # 블로그 본문 가져오기
    def test_get_blog_detail(self):
        url = reverse('blog:blog_detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['result']['title'], BLOG_DATA['title'])
        self.assertEqual(response.data['result']['view_count'], 1) # 조회수 증가 확인



class SubscribeTest(APITestCase):  
    def test_subscribe(self):
        url = reverse('blog:subscribe')
        response = self.client.post(url, {'email': 'test@ddsde.com'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue(response.data['result']['is_subscribed'])

        #이메일 중복이여도 오류 나지 않음
        response = self.client.post(url, {'email': 'test@ddsde.com'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue(response.data['result']['is_subscribed'])