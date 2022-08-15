'''
    Admin 사이트 설정
'''
from django.contrib import admin
from django.conf import settings
from django.contrib.admin.sites import AdminSite 
from django.core.exceptions import ValidationError


class MyAdminSite(AdminSite):
    site_header = 'Blog API 관리자'
    site_title = 'Blog API 관리자'
    index_title = 'Blog API 관리자'
    site_url = settings.SITE_URL
    enable_nav_sidebar = False

admin_site = MyAdminSite(name='Blog API 관리자')

class MyModelAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, extra_content=None):
        extra_context = extra_content or {}
        extra_context['show_save_and_add_another'] = False
        return super(MyModelAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def add_view(self, request, form_url=None, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super(MyModelAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)

# 오직 수정만 되는 페이지
class MyOnlyUpdateModelAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, extra_content=None):
        extra_context = extra_content or {}
        extra_context['show_save_and_add_another'] = False
        return super(MyOnlyUpdateModelAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def add_view(self, request, form_url=None, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super(MyOnlyUpdateModelAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def validate_file_size_lt_10mb(value): 
    limit = 10 * 1024 * 1024
    if value.size > limit:
        raise ValidationError({'file': '10MB 미만의 파일만 업로드할 수 있습니다.'})