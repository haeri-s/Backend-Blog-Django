from django.conf.urls import url
from django.urls import path
from blog.views import BlogView, UploadFroalaView, DeleteImageView, BlogListView, BlogBookmarkListView, SubscribView

app_name = 'blog'
urlpatterns = [
    path('', name='blog_list', view= BlogListView.as_view()),
    path('<int:pk>', name='blog_detail', view= BlogView.as_view()),
    path('bookmark', name='blog_bookmark', view= BlogBookmarkListView.as_view()),
    path('subscribe', name='subscribe', view= SubscribView.as_view()),
    path('upload/<str:file_type>', name='blog_upload_img', view= UploadFroalaView.as_view()),
    path('delete_image', name='blog_delete_img', view= DeleteImageView.as_view()),
]