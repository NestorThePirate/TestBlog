from article.models import Article
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import HitCount


@receiver(post_save, sender=Article)
def rating_model_save(sender, instance, **kwargs):
    if len(instance.hit_count_object.all()) < 1:
        HitCount.objects.create(content_object=instance)