from django import forms
from .models import Article
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist


class SearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False
    )


class ArticleForm(forms.Form):
    title = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)
    tag = forms.CharField()

    def __init__(self, *args, **kwargs):
        try:
            self.article = kwargs.pop('article')
        except KeyError:
            pass
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('The title is too short')
        try:
            Article.objects.get(title=title)
            if self.article is not None:
                pass
            else:
                raise forms.ValidationError('Статья с таким заголовком уже существует')
        except ObjectDoesNotExist:
            pass
        return title

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 150:
            raise forms.ValidationError('The text is too short')
        return text
