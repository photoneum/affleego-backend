from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'server.apps.users'
    verbose_name = 'Users'

    def ready(self):
        pass
