"""
Django settings for apiserver project.
"""

import os
import json
from datetime import timedelta
import io
import environ
from google.cloud import secretmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

############################# Environ Setting ##############################
env = environ.Env(DEBUG=(bool, False))
env_file = os.path.join(BASE_DIR, "../../.env")

if os.path.exists(env_file) and os.path.isfile(env_file):
    env.read_env(env_file)
    
# [START_EXCLUDE]
elif os.getenv("TRAMPOLINE_CI", None):
    placeholder = (
        f"SECRET_KEY=a\n"
        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
    )
    env.read_env(io.StringIO(placeholder))
# [END_EXCLUDE]

elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "blog-api-server")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    env.read_env(io.StringIO(payload))
else:
    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")


SECRET_KEY = os.environ.get('SECRET_KEY')
KAKAO = {
    'REST_API_KEY': os.environ.get('KAKAO_REST_API_KEY'),
    'API_KEY': os.environ.get('KAKAO_API_KEY'),
    'STORE_ID': os.environ.get('KAKAO_STORE_ID'),
    'CALLBACK': os.environ.get('KAKAO_CALLBACK'),
}

DEBUG = True
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    'storage.googleapis.com', 
    '0.0.0.0',
]
SITE_URL = 'http://127.0.0.1:3000'


############################# Application Setting ##############################
INSTALLED_APPS = [
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'rest_framework',  # rest api
    'corsheaders',  # rest api cors header 설정
    'django_extensions',  # django-adimin 확장 라이브러리
    'froala_editor',  # froala editor
    'imagekit', # imagekit 이미지
    'drf_yasg', # document
    'taggit',
    'taggit_labels',
    'taggit_templatetags2',
    
    'account',
    'blog',
    'django_inlinecss',
]

MIDDLEWARE = [
    "django_samesite_none.middleware.SameSiteNoneMiddleware",
    'apiserver.utils.middleware.TokenRefreshFromHeaderIntoTheBody',
    'corsheaders.middleware.CorsMiddleware',
    'request_logging.middleware.LoggingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]
ROOT_URLCONF = 'apiserver.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'apiserver.utils.utils.get_site_url',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'apiserver.wsgi.application'


############################# Password validation Setting ##############################
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]

############################# Database Setting ##############################
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': env.db()
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "HOST": os.environ.get("DB_HOST"),
            "PORT": os.environ.get("DB_PORT"),
        }
    }
    
if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
    DATABASES["default"]["HOST"] = "127.0.0.1"
    DATABASES["default"]["PORT"] = 5432


############################# Email Setting ##############################
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')


############################# Internationalization Setting ##############################
# https://docs.djangoproject.com/en/3.0/topics/i18n/
USE_TZ = False # true 일 경우 timezone.now() 를 사용해야 함
USE_L10N = True # format 활성s화
USE_I18N = True # 번역 활성화
TIME_ZONE = 'Asia/Seoul'  # django.utils.timezone.now()
LANGUAGE_CODE = 'ko'

DATE_FORMAT = '%Y.%m.%d'
TIME_FORMAT = '%H:%M'
DATETIME_FORMAT = '%Y.%m.%d %H:%M:%S'

THOUSAND_SEPARATOR = '\xa0'


########################## GCP STORAGE ##########################
STATIC_URL = '/apiserver/static/'
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
GS_DEFAULT_ACL='publicRead'
GS_PROJECT_ID= os.environ.get('GOOGLE_CLOUD_PROJECT', 'apiserver-15cc1')
DATA_UPLOAD_MAX_MEMORY_SIZE= 10 * 1028 * 1028 # 파일 최대 크기
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


############################# REST API Setting ##############################
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'apiserver.utils.customRestSetting.CustomJsonRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'apiserver.utils.customRestSetting.CustomLimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'EXCEPTION_HANDLER': 'apiserver.utils.customException.custom_exception_handler',
    # TEST
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

############################# JWT Setting ##############################
JWT_AUTH = {
    'JWT_ENCODE_HANDLER': 'rest_framework_jwt.utils.jwt_encode_handler',
    'JWT_DECODE_HANDLER': 'rest_framework_jwt.utils.jwt_decode_handler',
    'JWT_PAYLOAD_HANDLER': 'rest_framework_jwt.utils.jwt_payload_handler',
    'JWT_PAYLOAD_GET_USER_ID_HANDLER': 'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'account.serializers.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=30),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_AUTH_COOKIE': 'YDAUTH',
}


AUTH_USER_MODEL = 'account.User'

ACCOUNT_ACTIVATION_DAYS = 30  # days

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'

# 탈퇴회원(is_active=False)도 authenticate()에서 user return 받을 수 있게함
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend']
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


############################# DJANGO JET ADMIN Setting ##############################
X_FRAME_OPTIONS = 'SAMEORIGIN'
JET_SIDE_MENU_COMPACT = True

JET_THEMES = [
    {
        'theme': 'default',  # theme folder name
        'color': '#47bac1',  # color of the theme's button in user menu
        'title': 'Default'  # theme title
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]

JET_DEFAULT_THEME = 'default'


############################# FROALA EDITOR ##############################
FROALA_EDITOR_OPTIONS = {
    'apiKey': 'xGE6oD3H4B3B11B5C7fLUQZf1ASFb1EFRNh1Hb1BCCQDUHnA8B6E5C4B1C3E4A1A8A6==',
    'key': 'xGE6oD3H4B3B11B5C7fLUQZf1ASFb1EFRNh1Hb1BCCQDUHnA8B6E5C4B1C3E4A1A8A6==',
    'fontSize': 	['14', '16', '18', '20', '22', '24', '26', '28',  '30', '36', '48', '60', '72', '96'],
    'videoUpload': False,
    'language': 'ko',
    'height': 300,
    'imageMaxSize': 10 * 1024 * 1024,
    'imageAllowedTypes': ['jpeg', 'jpg', 'png'],
    # 'imageUploadURL': 'https://blog.apiserver.co/api/upload?type=notice&isImage=true',
    'imageUploadURL': '/api/v1/blogs/upload/image',
    'imageManagerLoadURL': '/api/v1/blogs/upload/image',
    'imageManagerDeleteURL': '/api/v1/blogs/delete_image',
    'fileUploadURL': '/api/v1/blogs/upload/file',
    'tableStyles': {
        'class1': 'default',
        'class2': 'grey'
    },
    'fileMaxSize': 10 * 1024 * 1024,
    'tableInsertHelperOffset': 5,
    'tableInsertMaxSize': 15,
    'toolbarButtons': {
        'moreText': {
        'buttons': ['bold', 'fontSize', 'textColor', 'italic', 'underline', 'strikeThrough', 'subscript', 'superscript', 'fontFamily', 'backgroundColor', 'inlineClass', 'inlineStyle', 'clearFormatting']
        },
        'moreParagraph': {
        'buttons': ['alignLeft', 'alignCenter', 'formatOLSimple', 'alignRight', 'alignJustify', 'formatOL', 'formatUL', 'paragraphFormat', 'paragraphStyle', 'lineHeight', 'outdent', 'indent', 'quote'],
        'buttonsVisible': 2
        },
        'moreRich': {
        'buttons': ['insertLink', 'insertImage', 'insertTable', 'emoticons', 'fontAwesome', 'specialCharacters', 'embedly', 'insertFile', 'insertHR'],
        'buttonsVisible': 2

        },
        'moreMisc': {
        'buttons': ['undo', 'redo', 'fullscreen', 'print', 'getPDF', 'spellChecker', 'selectAll', 'html', 'help'],
        'align': 'right',
        'buttonsVisible': 3
        }
    },
}


############################# TAGGIT SETTING ##############################
TAGGIT_CASE_INSENSITIVE = True # 태그 검색할 때 대소문자 구별 안함


########################## SWAGGER SETTINGS ##########################
SWAGGER_SETTINGS = {
    "DEFAULT_INFO": "apiserver.utils.customApiDocument.api_info",
    'DEFAULT_AUTO_SCHEMA_CLASS': 'apiserver.utils.customApiDocument.CustomSwaggerAutoSchema',
    'LOGIN_URL': "/admin/login",
    'LOGOUT_URL':"/admin/logout?next=/swagger",
}

