"""OWASP Nest base configuration."""

import os
from pathlib import Path

from configurations import Configuration, values

BASE_DIR = Path(__file__).resolve().parent.parent


class Base(Configuration):
    """Base configuration."""

    ALLOWED_HOSTS = values.ListValue()
    DEBUG = False
    ENVIRONMENT = os.environ.get("DJANGO_CONFIGURATION")

    DJANGO_APPS = (
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    )

    THIRD_PARTY_APPS = ("storages",)

    LOCAL_APPS = (
        "apps.common",
        "apps.github",
        "apps.owasp",
    )

    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "settings.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [BASE_DIR / "templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "wsgi.application"

    # Database
    # https://docs.djangoproject.com/en/5.1/ref/settings/#databases
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": values.Value(environ_name="DB_NAME"),
            "USER": values.Value(environ_name="DB_USER"),
            "PASSWORD": values.SecretValue(environ_name="DB_PASSWORD"),
            "HOST": values.Value(environ_name="DB_HOST"),
            "PORT": values.Value(environ_name="DB_PORT"),
        },
    }

    # Password validation
    # https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/5.1/topics/i18n/

    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/5.1/howto/static-files/
    STATIC_URL = "static/"

    # Default primary key field type
    # https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = values.SecretValue()

    # https://docs.djangoproject.com/en/5.1/ref/settings/#data-upload-max-number-fields
    DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

    STATIC_ROOT = BASE_DIR / "staticfiles"
