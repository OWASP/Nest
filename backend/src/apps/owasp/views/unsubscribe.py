"""One-click unsubscribe view for RFC 8058 (List-Unsubscribe-Post)."""

from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.owasp.models.snapshot_subscription import SnapshotSubscription


@method_decorator(csrf_exempt, name="dispatch")
class OneClickUnsubscribeView(View):
    """Handle RFC 8058 one-click unsubscribe from email clients like Gmail."""

    def post(self, request, token):
        """Process one-click unsubscribe POST request."""
        return self.unsubscribe(token)

    def get(self, request, token):
        """Handle GET request for browser-based unsubscribe."""
        return self.unsubscribe(token)

    def unsubscribe(self, token):
        """Delete the subscription matching the given token."""
        subscription = self.find_subscription(token)
        if subscription is None:
            return HttpResponse(status=404)

        subscription.delete()

        return JsonResponse({"message": "Successfully unsubscribed."}, status=200)

    @staticmethod
    def find_subscription(token):
        """Find a SnapshotSubscription by unsubscribe token."""
        try:
            return SnapshotSubscription.objects.get(unsubscribe_token=token)
        except (SnapshotSubscription.DoesNotExist, ValidationError):
            return None
