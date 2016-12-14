from django import forms
from .models import PrivateMessage


class MessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ('title', 'text', 'target_user')

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 1:
            raise forms.ValidationError('Заголовок слишком короткий')
        return title
