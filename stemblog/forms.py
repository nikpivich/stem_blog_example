from django import forms
from ckeditor.widgets import CKEditorWidget

from .models import News


class NewsForm(forms.Form):
    title = forms.CharField(label='Заголовок', required=True, max_length=100)
    image = forms.ImageField(required=False)
    content = forms.CharField(label='Содержание', required=True, widget=CKEditorWidget)


class NewsModelForms(forms.ModelForm):
    class Meta:
        model = News
        fields = [ 'title', 'image', 'content']
