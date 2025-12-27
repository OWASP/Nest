from apps.core.services.project_service import ProjectPublicDTO


def test_project_dto_sanitization():
    """Verify that ProjectPublicDTO sanitizes HTML inputs to prevent XSS."""
    unsafe_data = {
        "name": "<script>alert('xss')</script>Project",
        "url": 'http://example.com/" onclick="steal()',
        "description": "<b>Bold</b> but <img src=x onerror=alert(1)>",
        "maintainers": ["Alice", "<script>Bob</script>"],
    }

    dto = ProjectPublicDTO(**unsafe_data)

    assert "&lt;script&gt;" in dto.name
    assert "<script>" not in dto.name
    assert "&quot;" in dto.url
    assert "Alice" in dto.maintainers
    assert "&lt;script&gt;Bob&lt;/script&gt;" in dto.maintainers
