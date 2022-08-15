"""
    Api Document 맞춤 설정
"""

from drf_yasg import openapi
from collections import OrderedDict
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from django.conf import settings


api_info = openapi.Info(
    title="Blog API API",
    default_version='v1',
    description="Blog API API 입니다.",
    terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="blog@blog.com"),
    license=openapi.License(name="블로그 BLOG License"),
)

status_schema = ('status', openapi.Schema(description='success: 성공, error: 문제 발생', type=openapi.TYPE_STRING))
schema_view = get_schema_view(api_info, public=False, permission_classes=(permissions.IsAdminUser,))
if settings.DEBUG:
    schema_view = get_schema_view(api_info, public=True, permission_classes=(permissions.AllowAny,)  )


class CustomSwaggerAutoSchema(SwaggerAutoSchema):
    def get_default_responses(self):
        res = super().get_default_responses()

        for key, value in res.items():
            if value:
                if isinstance(value, openapi.Schema):
                    if(super().should_page()):
                        props = OrderedDict((
                            ('next', openapi.Schema('next', type=openapi.FORMAT_URI)),
                            ('previous', openapi.Schema('previous', type=openapi.FORMAT_URI)),
                            ('total', openapi.Schema('total', type=openapi.TYPE_INTEGER)),
                            ('data', value.properties['results'])
                        ))
                        if not len(super().get_pagination_parameters()):
                            props = OrderedDict((
                                ('data', value.properties['results']),
                            ))
                            
                        value.properties = openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties = props
                        )
                    if key[0] == '2':
                        value.properties = OrderedDict((
                            status_schema,
                            ('result', value.properties )
                        ))
                elif isinstance(value, openapi.SchemaRef):
                    value = openapi.Schema('result', 
                        properties=OrderedDict((
                            status_schema,
                            ('result', value),
                        )), type=openapi.TYPE_OBJECT)
            res[key] =  value

        return res


class ErrorCollection(object):
    def __init__(self, code, status, message):
        self.code = code
        self.status = status
        self.message = message
    
    def as_md(self):
        return '\n\n> **%s**\n\n```\n{\n\n\t"status": "error"\n\n\t"error_code": "%s"\n\n\t"detail": %s\n\n}\n\n```' % \
            (self.message, self.code, self.message)


user_login_schema = openapi.Schema(type=openapi.TYPE_OBJECT,
    properties=OrderedDict((
        status_schema,
        ('result', openapi.Schema(type=openapi.TYPE_OBJECT, properties=OrderedDict((
        ('token', openapi.Schema(type=openapi.TYPE_STRING)),
                ('user', openapi.Schema(type=openapi.TYPE_OBJECT, 
                    properties=OrderedDict((
                        ('id', openapi.Schema(type=openapi.FORMAT_UUID)),
                        ('email', openapi.Schema(type=openapi.TYPE_STRING)),
                        ('name', openapi.Schema(type=openapi.TYPE_STRING)),
                        ('phone_number', openapi.Schema(type=openapi.TYPE_STRING)),
                        ('provider', openapi.Schema(type=openapi.TYPE_STRING)),
                        ('is_staff', openapi.Schema(type=openapi.TYPE_BOOLEAN)),
                        ('is_active', openapi.Schema(type=openapi.TYPE_BOOLEAN)),
                    ))
                ))
        ))))
    ))
)


status_object_schema = openapi.Schema(type=openapi.TYPE_OBJECT,
    properties=OrderedDict((
        status_schema,
    ))
)

