from rest_framework.views import APIView
from rest_framework.response import Response
from owasp.models.snapshot import Snapshot

class SnapshotsSitemapView(APIView):
    """Sitemap view for snapshots."""

    def get(self, request, *args, **kwargs):
        snapshots = Snapshot.objects.all().order_by('-created_at')
        data = [
            {
                "id": snapshot.id,
                "title": snapshot.title,
                "key": snapshot.key,
                "created_at": snapshot.created_at,
                "status": snapshot.status,
                "start_at": snapshot.start_at,
                "end_at": snapshot.end_at,
                "error_message": snapshot.error_message,
            }
            for snapshot in snapshots
        ]
        return Response(data)
