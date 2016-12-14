from django.shortcuts import render
from .models import Hit
from .utils import get_ip


class HitCountMixIn(object):

    @classmethod
    def add_hit(cls, request, hit_counter):
        ip_address = get_ip(request)
        if request.session.session_key is None:
            request.session.save()

        user = request.user
        session_key = request.session.session_key
        if user.is_anonymous:
            username = 'Anonymous'
            user = None
        else:
            username = user.username

        hit = Hit.objects.get_or_create(hit_counter=hit_counter,
                                        ip=ip_address,
                                        session=session_key,
                                        user=user,
                                        username=username)
        hit[0].save()
        hit_counter.refresh_hits()
