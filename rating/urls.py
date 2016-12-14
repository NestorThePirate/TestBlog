from django.conf.urls import url
from . import views


urlpatterns = [
    url(regex='^rate/(?P<pk>[0-9]+)/(?P<like>[\w]+)/$',
        view=views.like_view,
        name='like-view')
]
