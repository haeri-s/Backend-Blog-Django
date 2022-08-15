import os
from google.oauth2 import service_account
from apiserver.settings.base import *

############################# Media SETTING ##############################
MEDIA_ROOT = os.path.join(BASE_DIR, '../../media')
MEDIA_URL = '/media/'

############################# Network SETTING ##############################
DEBUG = True
TEMPLATE_DEBUG=True
PAGE_CACHE_SECONDS = 1

# cors header
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000'
]
CORS_ALLOWED_ORIGINS= [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000'
]
REST_FRAMEWORK['TEST_REQUEST_RENDERER_CLASSES'] = (
    'rest_framework.renderers.MultiPartRenderer',
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.TemplateHTMLRenderer'
)

CSRF_COOKIE_SECURE = False # https 프로토콜에서만 브라우저가 서버로 쿠키를 포험해서 요청함
SESSION_COOKIE_SECURE = False # https 프로토콜에서만 브라우저가 서버로 쿠키를 포험해서 요청함
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'


################################# LOGGING SETTING ##########################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True, #기존의 로깅 설정을 비활성?
    
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(name)s %(asctime)s %(module)s '
                    '%(process)d %(thread)d %(message)s'
        },
        'fileFormat':{
            'format': '[%(asctime)s] %(name)s [%(levelname)s] %(message)s',
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
        #로그 파일 저장
        # 'file': {
        #     'level': 'ERROR',
        #     'class' : 'logging.handlers.RotatingFileHandler',
        #     'filename': os.path.join(BASE_DIR, '../../.log/log.log'),
        #     'maxBytes': 1024*1024*5, # 5 MB
        #     'backupCount': 30,
        #     'formatter':'fileFormat',
        #     'encoding' : 'utf-8'
        # },
    },
    'loggers': {
        'django_rest_logger': {
            'level': 'DEBUG',
            'handlers': ['django_rest_logger_handler'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'handlers': [ 'console'],
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


########################## GCP STORAGE SETTING ##########################
GS_BUCKET_NAME = 'apiserver-dev'
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, '../../config/apiserver_gcp.json')
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)