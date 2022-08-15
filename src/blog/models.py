from django.db import models
from froala_editor.fields import FroalaField
from taggit.managers import TaggableManager
from django.db.models.signals import pre_save, post_delete
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.dispatch import receiver
import calendar
import time

from apiserver.utils.utils import gcp_delete_file

def blog_directory_path(instance, filename):
    return f'blogs/imgs/{calendar.timegm(time.gmtime())}/{filename}'
    

class Blog(models.Model):
    STATUS_CHOICES = [('showing', '공개'), ('bookmark', '주목받는 이야기'), ('temp', '비공개')]
    class Meta:
        db_table = 'Blog'
        verbose_name = '블로그'
        verbose_name_plural='블로그 관리'

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, null=False, verbose_name='제목')    
    contents = FroalaField(verbose_name='본문')
    tags = TaggableManager(verbose_name='태그', blank=True)
    view_count = models.IntegerField(verbose_name='조회수', default=0)
    status = models.CharField(verbose_name='공개상태', max_length=8, choices=STATUS_CHOICES, default='showing')
    main_img = models.ImageField(verbose_name='메인 이미지 경로', null=True, blank=True, upload_to=blog_directory_path)
    thumb_img = ImageSpecField(source='main_img', processors=[ResizeToFill(829, 486)], format='JPEG', options={'quality': 95})
    mobile_img = ImageSpecField(source='main_img', processors=[ResizeToFill(449, 263)], format='JPEG', options={'quality': 95})

    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True) 
    updated_at = models.DateTimeField(verbose_name='정보수정일시', auto_now=True) 

    def __str__(self):
        return '{}({})'.format(self._meta.verbose_name, self.id)
        

@receiver(post_delete, sender=Blog)
def post_delete_image(sender, instance, *args, **kwargs):
    if instance.main_img:
        gcp_delete_file(instance.main_img.name)

@receiver(pre_save, sender=Blog)
def pre_save_image(sender, instance, *args, **kwargs):
    try:
        old_img = instance.__class__.objects.get(id=instance.id).main_img
        try:
            new_img = instance.main_img
        except:
            new_img = None

        if old_img and new_img != old_img.name.split('/')[-1]:
            gcp_delete_file(old_img.name)
    except Exception as err:
        pass


class Subscribe(models.Model):
    class Meta:
        db_table = 'Subscribe'
        verbose_name = '뉴스레터 구독 목록'
        verbose_name_plural='뉴스레터 구독 관리'

    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name='이메일 주소', max_length=255, unique=True)
    is_subscribed = models.BooleanField(default=True, verbose_name="구독 여부") 
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True) 
    updated_at = models.DateTimeField(verbose_name='정보수정일시', auto_now=True) 

    def __str__(self):
        return '{}({})'.format(self._meta.verbose_name, self.id)