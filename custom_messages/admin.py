from django.contrib import admin
from .models import PrivateMessagesList, PrivateMessage


admin.site.register(PrivateMessagesList)
admin.site.register(PrivateMessage)
