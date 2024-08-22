"""GitHub app utils."""


def get_is_owasp_site_repository(key):
    """Identify OWASP site repository."""
    return key.startswith(
        (
            "www-chapter-",
            "www-committee-",
            "www-event",
            "www-project-",
        )
    )


def get_node_id(node):
    """Extract node_id."""
    return node.raw_data["node_id"]
