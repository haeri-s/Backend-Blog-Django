from rest_framework.pagination import CursorPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, JSONOpenAPIRenderer, BaseRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import models

# API 설정

class CustomLimitOffsetPagination(LimitOffsetPagination):
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = None
    default_limit = 9
    
    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'result': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'total': self.count,
                'data': data
            }
        })


class CustomCursorPagination(CursorPagination):
    page_size = 3
    ordering = '-updated_at'   
    cursor_query_param = None

    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'result': {
                'data': data
            }
        })
    
    def get_schema_fields(self, view): # Parameter 없음
        return []


class CustomJsonRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data or( not data.get('status', None) and isinstance(data, dict) and not 'link' in data.keys()):
            data = {
                'status': 'success',
                'result': data
            }
        return super().render(data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)
