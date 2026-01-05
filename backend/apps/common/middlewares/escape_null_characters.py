"""OWASP Nest Middleware to escape null characters in request data."""

from django.http import HttpRequest, HttpResponse


class EscapeNullCharactersMiddleware:
    """Escape null characters in request body, GET, and POST data."""

    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and return the response."""
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request: HttpRequest) -> None:
        """Process the incoming request and escape null characters."""
        if hasattr(request, "_body"):
            # ruff: noqa: SLF001
            request._body = request.body.replace(b"\x00", b"")

        if request.GET:
            request.GET = request.GET.copy()
            for key in request.GET:
                request.GET[key] = request.GET[key].replace("\x00", "")

        if request.POST:
            request.POST = request.POST.copy()
            for key in request.POST:
                request.POST[key] = request.POST[key].replace("\x00", "")
