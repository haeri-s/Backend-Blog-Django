import os

from apiserver.settings.base import *
from google.oauth2 import service_account
from urllib.parse import urlparse

############################# Network SETTING ##############################
DEBUG = False
TEMPLATE_DEBUG = DEBUG

PAGE_CACHE_SECONDS = 1200
TIMEOUT=500

CORS_ALLOWED_ORIGINS=[
    'https://storage.googleapis.com',
    'https://blog.co.kr',
    'https://stage.blog.co.kr',
]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOWED_ORIGINS=[
    'https://storage.googleapis.com',
    'https://blog.co.kr',
    'https://stage.blog.co.kr',
    'https://blog.blog.co.kr',
    'https://stage-web-aw75eq6opq-du.a.run.app',
    'https://blog-aw75eq6opq-du.a.run.app'
]

# SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SITE_URL =  'https://blog.co.kr'
ALLOWED_HOSTS= [
    'storage.googleapis.com', 
    'stage.blog.co.kr',
    'blog.co.kr',
    'apiserver-aw75eq6opq-du.a.run.app'
]

################################# Gloud Run Setting ##########################################
CLOUDRUN_SERVICE_URL = env("CLOUDRUN_SERVICE_URL", default=None)
if CLOUDRUN_SERVICE_URL:
    ALLOWED_HOSTS = [urlparse(CLOUDRUN_SERVICE_URL).netloc]
    CSRF_TRUSTED_ORIGINS = [CLOUDRUN_SERVICE_URL]
    SECURE_SSL_REDIRECT = True
else:
    ALLOWED_HOSTS = ["*"]


REST_FRAMEWORK['TEST_REQUEST_RENDERER_CLASSES'] = (
    'rest_framework.renderers.MultiPartRenderer',
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.TemplateHTMLRenderer'
)

########################## GCP STORAGE MEDIA Setting ##########################
GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME', 'apiserver-dev')
STATIC_URL = "/static/"
STATIC_ROOT="/static"
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, '../../config/apiserver_gcp.json')
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

################################# LOGGING Setting ##########################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True, #기존의 로깅 설정을 비활성
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(name)s %(asctime)s %(module)s '
                    '%(process)d %(thread)d %(message)s'
        },
        'fileFormat':{
            'format': '[%(asctime)s] %(name)s %(levelname)s %(message)s',
            'datefmt': '%Y/%b/%d %H:%M:%S'
        }
    },
    #로그 레코드로 무슨 작업 할 것인지 정의
    'handlers': {
        'django_rest_logger_handler': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        #콘솔 출력
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'fileFormat',
        },
    },
    'loggers': {
        'django_rest_logger': {
            'level': 'ERROR',
            'handlers': ['django_rest_logger_handler'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # change debug level as appropiate
            'propagate': False,
        },
        '': {
            'level': 'ERROR',
            'handlers': ['console'],
        }
    },
}

DEFAULT_LOGGER = 'django_rest_logger'

LOGGER_EXCEPTION = DEFAULT_LOGGER
LOGGER_ERROR = DEFAULT_LOGGER
LOGGER_WARNING = DEFAULT_LOGGER
LOGGER_INFO = DEFAULT_LOGGER
LOGGER_DEBUG = DEFAULT_LOGGER