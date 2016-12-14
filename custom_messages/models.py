from django.db import models
from django.conf import settings
from django.utils import timezone
from django.conf import settings


class PrivateMessagesList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_messages = models.IntegerField(default=0)
    checked_messages = models.IntegerField(default=0)
    unchecked_messages = models.IntegerField(default=0)
    income_messages = models.IntegerField(default=0)
    outcome_messages = models.IntegerField(default=0)

    def __str__(self):
        return 'PML of {0}'.format(self.user)

    def messages_counter(self):
        return '{0}/{1}'.format(self.unchecked_messages, self.checked_messages)


class PrivateMessage(models.Model):
    user_messages_list = models.ForeignKey(PrivateMessagesList, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField()
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='target')
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author')
    created = models.DateTimeField(default=timezone.now)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return 'Private message {0} from {1} to {2}'.format(self.title,
                                                            self.author_user,
                                                            self.target_user,
                                                            )
