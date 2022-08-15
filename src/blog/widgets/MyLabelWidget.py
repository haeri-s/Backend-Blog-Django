from taggit_labels.widgets import LabelWidget
from django import forms

class MyLabelWidget(LabelWidget):
    input_type = 'hidden'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs={}, renderer=None, **kwargs):
        res = super().render(name, value, attrs={}, renderer=None, **kwargs)
        # print(res)
        # return mark_safe(u"<input{0}{1}".format(res_split[1], res_split[0]))
        return '<input type="text" id="new_tag_input" style="min-width: 400px; margin-bottom: 10px;" placeholder="새로운 태그를 입력해주세요.(여러개일 경우 , 로 구분해주세요.)"  >' + res
    
    
    @property
    def media(self):
        old = super().media
        js = old._js
        js.append('js/tag_input.js')
        return forms.Media(js=js, css={"all": ("taggit_labels/css/taggit_labels.css",)})