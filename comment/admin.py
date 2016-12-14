from django.contrib import admin
from .models import CommentModel


class CommentExpand(admin.ModelAdmin):
    list_display = ('__str__', 'parent', 'user', 'get_score', 'created', 'edited')

admin.site.register(CommentModel, CommentExpand)
