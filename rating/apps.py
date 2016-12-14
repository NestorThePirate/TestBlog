from django.apps import AppConfig


class RatingConfig(AppConfig):
    name = 'rating'
    verbose_name = 'rating_application'

    def ready(self):
        import rating.signals
