from django.contrib.admin.decorators import register
from apiserver.admin import MyModelAdmin, MyOnlyUpdateModelAdmin, admin_site
from django import forms
from blog.models import Blog, Subscribe
from taggit.forms import TagField
from .widgets.MyLabelWidget import MyLabelWidget
from taggit.models import Tag
from django.db.models import Count

class CounterTextInput(forms.TextInput):
    template_name = 'count_text.html'


class ContentForm(forms.ModelForm):
    tags = TagField(required=False, widget=MyLabelWidget)
    
    class Meta:
        model = Blog
        exclude = []

@register(Blog, site=admin_site)
class BlogAdmin(MyModelAdmin):
    list_display = ('title', 'tag_list', 'status', 'created_at')
    search_fields = ['title']
    form = ContentForm
    readonly_fields = ['view_count']
    ordering = ['-created_at', 'status']
    list_filter = ('status', )
    # list_filter = ['tags']
    # fieldsets = (
    #     (None, {'fields': ('title', 'contetns', 'tags')}),
    # )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
    
    def tag_list(self, obj):
        if obj.tags:
            return '#' + ', #'.join(o.name for o in obj.tags.all())
        else:
            return ''

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        Tag.objects.annotate(ntag=Count('taggit_taggeditem_items')).filter(ntag=0).delete()
        return 


@register(Subscribe, site=admin_site)
class SubscribeAdmin(MyOnlyUpdateModelAdmin):
    list_display = ('email', 'is_subscribed', 'created_at', 'updated_at')
    ordering = ['-updated_at']
    readonly_fields = ('email', 'created_at', 'updated_at')