from django.apps import AppConfig


class usersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals # noqa
