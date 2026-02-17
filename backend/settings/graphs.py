from .local import Local


class Graphs(Local):
    INSTALLED_APPS = list(Local.INSTALLED_APPS)

    if "django_extensions" not in INSTALLED_APPS:
        INSTALLED_APPS.append("django_extensions")