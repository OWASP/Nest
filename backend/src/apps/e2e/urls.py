"""E2E app URL configuration."""

from django.urls import path

from apps.e2e.views import e2e_login

app_name = "e2e"

urlpatterns = [
    path("login/", e2e_login, name="login"),
]
