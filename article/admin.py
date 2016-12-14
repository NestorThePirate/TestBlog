from django.contrib import admin
from .models import Article, Subscription


class ArticleExpand(admin.ModelAdmin):
    list_display = ('__str__', 'title', 'user', 'created', 'edited')


admin.site.register(Article, ArticleExpand)
admin.site.register(Subscription)

