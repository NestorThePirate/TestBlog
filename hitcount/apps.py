from django.apps import AppConfig


class HitcountConfig(AppConfig):
    name = 'hitcount'

    def ready(self):
        import hitcount.signals
