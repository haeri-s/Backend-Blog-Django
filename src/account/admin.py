import datetime
from django.contrib import admin
from django.contrib.admin.decorators import register
from apiserver.admin import admin_site
from django import forms
from account.models import User

# 회원 관리
class UserAdmin(admin.ModelAdmin):
    
    list_display = ('email',  'name', 'phone_number', 'provider', 'is_staff', 'is_active', 'created_at', 'last_login')
    search_fields = ['email', 'name']
    list_filter = ('is_active', 'is_staff')
    date_hierarchy = 'created_at'
    ordering = ['-is_active', 'last_login', 'email']
    fieldsets = (('회원정보', {
        'fields': (('email', 'provider'), ('name', 'phone_number'), ('is_staff', 'is_superuser'), 'is_active', 'created_at', 'last_login', 'updated_at')
    }),)
    readonly_fields = [
        'is_active', 'provider', 'created_at', 'updated_at', 'last_login'
    ]

    def delete_model(self, request, obj):
        obj.is_active = False
        obj.deleted_at = datetime.datetime.now()
        obj.name = ''
        obj.phone_number = None
        obj.save()
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.is_staff = True if form.data.get('is_staff', None) == 'on' else False
            obj.is_superuser = True if form.data.get('is_superuser', None) == 'on' else False
        else:
            obj.set_password(form.data['password'])
            obj.is_staff = True
        
        obj.save(update_fields=['is_staff', 'is_superuser'])

        return super(UserAdmin,self).save_model(request, obj, form, change)

    def add_view(self,request, extra_content=None):
        self.fieldsets = (('관리자 회원 추가', {
            'fields': ('email', 'password', 'name', 'phone_number', ( 'is_superuser'),),
            'description': '<span style="color:red; font-size:13px; padding: 10px;">❗️ 일반 회원이 아닌 직원만 추가할 수 있습니다.</span>'
        }) ,)
        self.inlines = []
        try:
            self.readonly_fields.remove('email')
        except Exception as err:
            print(err)
            pass
        extra_context = extra_content or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super(UserAdmin,self).add_view(request, extra_context=extra_context)
    
    
    def change_view(self, request, object_id, extra_content=None):
        self.fieldsets = (('회원정보', {
                'fields': (('email', 'provider'), 'name', 'phone_number', ('is_staff', 'is_superuser'), 'is_active', 'created_at', 'last_login', 'updated_at')
            }),)
        self.readonly_fields.append('email')
        extra_context = extra_content or {}
        extra_context['show_save_and_add_another'] = False
        return super(UserAdmin,self).change_view(request, object_id, extra_context=extra_context)


admin_site.disable_action('delete_selected')
admin_site.register(User, UserAdmin)