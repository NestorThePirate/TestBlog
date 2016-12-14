from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Введите адрес электронной почты')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            password=password
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            username,
            email,
            password
            )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
    )
    username = models.CharField(
        verbose_name='username',
        max_length=30,
        unique=True
    )
    username_slug = models.CharField(blank=True, null=True, max_length=30, unique=True)
    is_active = models.BooleanField(default=False, verbose_name='activation')
    is_admin = models.BooleanField(default=False, verbose_name='Admin permission')
    registration_date = models.DateTimeField(default=timezone.now, verbose_name='registration date')
    avatar = models.ImageField(blank=True, null=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        self.username_slug = self.username.lower()
        super().save(*args, **kwargs)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def get_user_articles(self):
        from article.models import Article
        return Article.objects.filter(user=self)

    def get_user_comments(self):
        from comment.models import CommentModel
        return CommentModel.objects.filter(user=self)

    def get_last_comment_created(self):
        return self.get_user_comments().last().created

    def get_user_tag(self):
        from tag.models import Tag
        return Tag.objects.filter(user=self)

    def get_user_rating_object(self):
        return self.userrating

    def get_user_likes(self):
        return self.get_user_rating_object().likes

    def get_user_dislikes(self):
        return self.get_user_rating_object().dislikes

    def get_user_rating(self):
        return self.userrating.score

    def get_subscriptions(self):
        from article.models import Subscription
        return Subscription.objects.filter(subscribed_user=self)

    def get_subscription_articles(self):
        articles = []
        for s in self.get_subscriptions():
            articles.append(s.article)
        return articles

    def update_subscriptions(self):
        for sub in self.get_subscriptions():
            sub.get_updates()

    def get_previous_comments(self):
        from comment.models import CommentModel
        return CommentModel.objects.filter(user=self)[:5]

    def get_previous_articles(self):
        from article.models import Article
        return Article.objects.filter(user=self)[:5]

    def get_private_messages_list(self):
        return self.privatemessageslist

    def get_messages(self):
        return self.get_private_messages_list().privatemessage_set.all()

    def get_unchecked_messages(self):
        return self.get_private_messages_list().unchecked_messages

    def get_income_messages(self):
        return self.get_private_messages_list().privatemessage_set.filter(target_user=self)

    def get_outcome_messages(self):
        return self.get_private_messages_list().privatemessage_set.filter(author_user=self)

    @staticmethod
    def update_current_subscription(sub):
        sub.subscription_opened()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
