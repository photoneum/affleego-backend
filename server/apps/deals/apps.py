from django.apps import AppConfig


class DealsConfig(AppConfig):
    name = 'server.apps.deals'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        pass
