from django.apps import AppConfig


class CustomMessagesConfig(AppConfig):
    name = 'custom_messages'

    def ready(self):
        import custom_messages.signals
