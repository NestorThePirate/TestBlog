from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

import datetime


class HitCount(models.Model):
    hits = models.IntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.SlugField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created = models.DateTimeField(default=timezone.now)
    edited = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return 'Hits of {0}'.format(self.content_object)

    def save(self, *args, **kwargs):
        self.edited = timezone.now()
        super().save(*args, **kwargs)

    def get_period_hits(self, **kwargs):
        period = timezone.now() - datetime.timedelta(**kwargs)
        return len(self.hit_set.filter(created_gte=period))

    def refresh_hits(self):
        self.hits = self.hit_set.all().count()
        self.save()

    class Meta:
        verbose_name = 'Hit Counter'
        verbose_name_plural = 'Hit Counters'


class Hit(models.Model):
    hit_counter = models.ForeignKey(HitCount, verbose_name='hit counter model')
    ip = models.CharField(max_length=40, editable=False)
    session = models.CharField(max_length=40, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    username = models.CharField(max_length=45)

    created = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super(Hit, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Hit, self).delete(*args, **kwargs)
