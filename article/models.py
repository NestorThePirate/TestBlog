from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from rating.models import RatingModel
from hitcount.models import HitCount
from django.conf import settings
from django.shortcuts import reverse
from django.utils.text import slugify


class ArticleManager(models.Manager):
    def get_popular_articles(self):
        return Article.objects.all().order_by('hit_count_object__hits')


class Article(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    pretext = models.TextField(max_length=1000)
    image = models.ImageField(blank=True, null=True)

    created = models.DateTimeField(default=timezone.now)
    edited = models.DateTimeField(blank=True, null=True)

    rating_object = GenericRelation(RatingModel)
    hit_count_object = GenericRelation(HitCount)

    primary_key = models.SlugField(primary_key=True,
                                   max_length=250,
                                   unique=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def save(self, *args, **kwargs):
        self.edited = timezone.now()
        self.primary_key = slugify(self.title)
        self.pretext = self.text[:200]
        super().save(*args, **kwargs)

    objects = ArticleManager()

    def __str__(self):
        return 'Article PK: {0}'.format(self.primary_key)

    def sidebar_info(self):
        return 'Тема: {0} {1}'.format(self.title, self.created)

    def get_absolute_url(self):
        return reverse('article-details', args=[str(self.primary_key)])

    def get_article_rating_model(self):
        return self.rating_object.last()

    def get_article_rating_model_id(self):
        return self.rating_object.last().pk

    def get_article_score(self):
        return self.rating_object.last().score

    def get_likes(self):
        return self.rating_object.last().vote_set.filter(like=True).count()

    def get_dislikes(self):
        return self.rating_object.last().vote_set.filter(like=False).count()

    def get_comment_list(self):
        return self.commentmodel_set.all()

    def get_number_of_comments(self):
        return len(self.commentmodel_set.all())

    def get_hit_counter(self):
        return self.hit_count_object.last()

    def get_hits(self):
        return self.hit_count_object.last().hit_set.all().count()


class Subscription(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    subscribed_user = models.OneToOneField('user.CustomUser', on_delete=models.CASCADE)
    updates_counter = models.SmallIntegerField(default=0)
    watched_comments = models.SmallIntegerField(default=0)

    def subscription_opened(self):
        self.updates_counter = 0
        self.watched_comments = len(self.article.commentmodel_set.all())
        self.save()

    def get_updates(self):
        self.updates_counter = len(self.article.commentmodel_set.all()) - self.watched_comments
        self.save()

    def __str__(self):
        return 'Subscription on {0}'.format(self.article.title)

    def get_absolute_url(self):
        return reverse('article-details', args=[self.article.primary_key])

    def get_last_comments(self):
        return self.article.commentmodel_set.all()[:5]
