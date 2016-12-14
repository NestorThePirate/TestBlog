from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from user.models import CustomUser


class UserRating(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def get_child_rating_objects(self):
        return self.ratingmodel_set.all()

    def calculate_score(self):
        child_rating_objects = self.get_child_rating_objects()
        likes = child_rating_objects.aggregate(models.Sum('likes'))
        dislikes = child_rating_objects.aggregate(models.Sum('dislikes'))
        self.likes = likes['likes__sum']
        self.dislikes = dislikes['dislikes__sum']
        self.score = self.likes - self.dislikes
        self.save()


class RatingModel(models.Model):
    user_rating = models.ForeignKey(UserRating, on_delete=models.CASCADE)

    score = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='tied object')
    object_id = models.SlugField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created = models.DateTimeField(default=timezone.now)
    edited = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        if self.content_object == 'Article':
            obj = self.content_object.primary_key
        else:
            obj = self.content_object.pk
        return 'Rating model for: {0} ID: {1}'.format(self.content_type, obj)

    def save(self, *args, **kwargs):
        self.edited = timezone.now()
        super().save(*args, **kwargs)

    def calculate_score(self):
        self.likes = len(self.vote_set.filter(like=True))
        self.dislikes = len(self.vote_set.filter(like=False))

        self.score = self.likes - self.dislikes
        self.save()
        self.user_rating.calculate_score()


class Vote(models.Model):
    target = models.ForeignKey(RatingModel, on_delete=models.CASCADE)
    like = models.BooleanField(default=True)
    user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE)

    created = models.DateTimeField(default=timezone.now)
    edited = models.DateTimeField(blank=True, null=True)

    def change_like(self):
        if self.like is True:
            self.like = False
        else:
            self.like = True
        self.save()
