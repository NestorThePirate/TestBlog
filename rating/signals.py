from article.models import Article
from .models import RatingModel, UserRating
from comment.models import CommentModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist


@receiver(post_save, sender=Article)
@receiver(post_save, sender=CommentModel)
def rating_model_save(sender, instance, **kwargs):
    if len(instance.rating_object.all()) < 1:
        RatingModel.objects.create(content_object=instance,
                                   user_rating=instance.user.get_user_rating_object())


@receiver(post_save, sender=RatingModel)
def user_rating_change(sender, instance, **kwargs):
    instance.user_rating.calculate_score()


@receiver(post_save, sender=CustomUser)
def user_rating_object_create(sender, instance, **kwargs):
    try:
        UserRating.objects.get(user=instance)
    except ObjectDoesNotExist:
        UserRating.objects.create(user=instance)
