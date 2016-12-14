from django import forms
from .models import CommentModel
from django.utils import timezone


class CommentForm(forms.ModelForm):
    parent = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'parent'}), required=False)

    class Meta:
        model = CommentModel
        fields = ('text', )
        help_texts = {
            'text': 'Оставить сообщение',
        }
        labels = {
            'text': '',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) <= 1:
            raise forms.ValidationError('текст слишком короткий')
        return text
