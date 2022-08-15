import os, datetime
from django.conf import settings
from rest_framework_jwt.settings import api_settings
from django.core.files.storage import default_storage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 기본 SITE URL 가져오기
def get_site_url(request):
    return {'SITE_URL': settings.SITE_URL}

# Header Cookies 에 token 정보 저장
def set_token_in_cookies(res, token, expiration=None):
    if api_settings.JWT_AUTH_COOKIE:
        if not expiration:
            expiration = (datetime.datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA)
        res.set_cookie(api_settings.JWT_AUTH_COOKIE,
                        token,
                        expires=expiration,
                        httponly=True, samesite=None, secure=True)

    return res

# Header Cookies 에 token 정보 삭제
def delete_token_in_cookies(res):
    res.delete_cookie(settings.CSRF_COOKIE_NAME)
    res.delete_cookie('sessionid')
    res.delete_cookie(api_settings.JWT_AUTH_COOKIE)
    return res

# 파일 확장자 확인
def check_file_ext(file, is_img = False):
    try:
        ext = file.content_type
        ext = ext.split('/')[-1].lower()
        stand = ['jpeg', 'jpg', 'png'] if is_img else ['jpeg', 'jpg', 'png', 'doc', 'docs', 'hwp', 'zip', 'pdf']
        if ext in stand:
            return True
        return False
    except:
        return False

# 파일 용량 확인
def check_file_size(file, stand = 10):
    try:
        if file.size < stand * 1028 * 1028:
            return True
        return False
    except:
        return False

# GCP Storage에 파일 업로드
def gcp_upload_file(file, path):
    path = default_storage.save(path, file)
    path = default_storage.url(path)
    return path

# GCP Storage 파일 삭제
def gcp_delete_file(path):
    if default_storage.exists(path):
        return default_storage.delete(path)
    return

