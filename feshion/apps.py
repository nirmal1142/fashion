from django.apps import AppConfig


class FeshionConfig(AppConfig):
    name = 'feshion'

    def ready(self):
        # import signal handlers
        import feshion.signals

