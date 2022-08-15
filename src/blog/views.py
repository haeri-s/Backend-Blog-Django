from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from blog.serializers import Blog, BlogDetailSerializer, BlogSerializer, SubscribeSerializer, Subscribe
import sys
import calendar
import time
from apiserver.utils.customRestSetting import CustomCursorPagination
from apiserver.utils.utils import check_file_ext, check_file_size, gcp_delete_file, gcp_upload_file

class UploadFroalaView(APIView):
    swagger_schema = None

    def post(self, request, file_type):
        try:
            file = request.FILES.get('file')
            response = {}
            is_img = file_type == 'image'
            if check_file_ext(file, is_img=is_img):
                if check_file_size(file):
                    path = 'utils/blogs/contents/{}/{}_{}'.format('imgs' if is_img else 'files', calendar.timegm(time.gmtime()), file.name)
                    path = gcp_upload_file(file, path)
                    response = {'link': path}
                else:
                    response = {'error': '10MB 보다 큰 파일은 올릴 수 없습니다.'}
            else:
                response = {'error': '지원하지 않는 확장자입니다.'}
        except Exception:
            response = {"error": str(sys.exc_info()[1])}
        return Response(response, status=status.HTTP_200_OK)


class DeleteImageView(APIView):
    swagger_schema = None

    def post(self, request):
        try:
            src = request.data.get('src')
            print(src)
            gcp_delete_file(src)
            Response(status=status.HTTP_200_OK)
        except Exception:
            response = {"error": str(sys.exc_info()[1])}
            print(Exception)
        return Response(response, status=status.HTTP_200_OK)

@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_id='blog_post_detail',
    operation_summary='블로그 본문 API',
    operation_description='블로그 가져오기'
))
class BlogView(RetrieveAPIView):
    serializer_class = BlogDetailSerializer
    permission_classes = (AllowAny,)
    queryset = Blog.objects.exclude(status='temp')

    def get(self, request, pk):
        # try:
        blog = self.queryset.get(pk=pk)
        blog.view_count += 1
        blog.save()
        return Response({'status': 'success', 'result': self.serializer_class(blog).data}, status=status.HTTP_200_OK)



@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_id='blog_list',
    operation_summary='블로그 목록 API',
    operation_description='블로그 목록 가져오기'
))
class BlogListView(ListAPIView):
    # pagination_class = LimitOffsetPagination
    serializer_class = BlogSerializer
    permission_classes = (AllowAny,)
    queryset = Blog.objects.exclude(status='temp').order_by('-created_at')

    def get_queryset(self):
        request = self.request
        keyword = request.GET.get('keyword')
        if keyword and len(keyword):
            return super().get_queryset().filter(title__contains=keyword)
        return super().get_queryset()



@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_id='blog_bookmark_list',
    operation_summary='자주찾는 블로그 목록 API',
    operation_description='자주찾는 블로그 목록 가져오기'
))
class BlogBookmarkListView(ListAPIView):
    pagination_class = CustomCursorPagination
    serializer_class = BlogSerializer
    permission_classes = (AllowAny,)
    queryset = Blog.objects.exclude(status='temp').filter(status='bookmark').order_by('-created_at')



class SubscribView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SubscribeSerializer

    @swagger_auto_schema(
        operation_id='subscribe_newsletter',
        operation_summary='뉴스레터 구독 API',
        operation_description='뉴스레터 구독하기'
        )
    def post(self, request):
        email = request.data.get('email', None)
        if not email:
            raise ValidationError({'detail': {'email': '이메일 정보가 없습니다.'}})
        try:
            ins = Subscribe.objects.get(email=email)
            serializer = self.serializer_class(instance=ins, data={'email': email, 'is_subscribed': True})
        except:
            serializer = self.serializer_class(data={'email': email})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        
        return Response({'status': 'success', 'result': serializer.data}, status=status.HTTP_201_CREATED)
        