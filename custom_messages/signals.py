from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from user.models import CustomUser
from .models import PrivateMessagesList, PrivateMessage


@receiver(post_save, sender=CustomUser)
def build_messages_list(sender, instance, **kwargs):
    PrivateMessagesList.objects.get_or_create(user=instance)


@receiver(post_save, sender=PrivateMessage)
@receiver(post_delete, sender=PrivateMessage)
def update_messages_list(sender, instance, **kwargs):
    private_message_list = instance.user_messages_list

    private_message_list.total_messages = len(private_message_list.privatemessage_set.all())

    private_message_list.checked_messages = len(private_message_list.privatemessage_set.filter(checked=True))

    private_message_list.unchecked_messages = private_message_list.total_messages - \
                                              private_message_list.checked_messages

    private_message_list.outcome_messages = len(private_message_list.privatemessage_set.
                                                filter(author_user=instance.author_user))

    private_message_list.income_messages = len(private_message_list.privatemessage_set.
                                               filter(target_user=instance.target_user))
    private_message_list.save()
