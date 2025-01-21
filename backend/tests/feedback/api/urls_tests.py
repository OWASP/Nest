from django.urls import resolve, reverse
from rest_framework.test import SimpleTestCase

from apps.feedback.api.feedback import FeedbackViewSet


class FeedbackURLsTest(SimpleTestCase):
    def test_feedback_list_url_is_resolved(self):
        url = reverse("feedback-list")
        assert resolve(url).func.cls == FeedbackViewSet

    def test_feedback_detail_url_is_resolved(self):
        url = reverse("feedback-detail", args=[1])
        assert resolve(url).func.cls == FeedbackViewSet
