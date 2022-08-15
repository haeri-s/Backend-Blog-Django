from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from blog.models import Blog, Subscribe


class BlogDetailSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    thumb_img = serializers.ImageField(read_only=True)
    mobile_img = serializers.ImageField(read_only=True)

    class Meta:
        model = Blog
        fields = ( 'id', 'title', 'contents', 'tags', 'view_count', 'main_img', 'thumb_img', 'mobile_img', 'created_at')
        # swagger_schema_fields = blog_detail_schema_fields

class BlogSerializer(TaggitSerializer, serializers.ModelSerializer):
    thumb_img = serializers.ImageField(read_only=True)
    mobile_img = serializers.ImageField(read_only=True)
    status_label = serializers.CharField(source='get_status_display')

    class Meta:
        model = Blog
        fields = ( 'id', 'title', 'status', 'status_label', 'thumb_img', 'mobile_img', 'created_at')

class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Subscribe
        fields = '__all__' 
