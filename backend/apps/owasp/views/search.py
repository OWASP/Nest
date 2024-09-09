"""OWASP app search views."""

from django.shortcuts import render


def search_issues(request):
    """Search issues view."""
    context = {
        "message": "Hello, world!",
        "items": ["Item 1", "Item 2", "Item 3"],
    }

    return render(request, "search/issues.html", context)
