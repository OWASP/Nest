from django.apps import apps
from django.test import SimpleTestCase

from apps.feedback.apps import FeedbackConfig


class FeedbackConfigTests(SimpleTestCase):
    def test_apps(self):
        assert FeedbackConfig.name == "apps.feedback"
        assert apps.get_app_config("feedback").name == "apps.feedback"
