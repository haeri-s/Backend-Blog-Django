"""
apiserver URL Configuration
"""
from django.conf import settings
from apiserver.admin import admin_site
from django.urls import path, include, re_path
from apiserver.utils.customApiDocument import schema_view
from django.conf.urls.static import static
from rest_framework.response import Response
from rest_framework import status


urlpatterns = [
    path('froala_editor/',include('froala_editor.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui( cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    path('admin/', admin_site.urls),
    path(r'api/v1/account/', include('account.urls')),
    path(r'api/v1/blogs/', include('blog.urls')),
    path("readiness_check", lambda r: Response("OK", status=status.HTTP_200_OK)),
    path("liveness_check", lambda r: Response("OK", status=status.HTTP_200_OK))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)