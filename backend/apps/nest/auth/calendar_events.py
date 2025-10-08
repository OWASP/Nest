"""Nest calendar events authorization permissions."""

from apps.owasp.models.entity_member import EntityMember
from apps.slack.models.member import Member


def has_calendar_events_permission(slack_user_id: str):
    """Check if a user has permission to access calendar events feature."""
    try:
        member = Member.objects.get(slack_user_id=slack_user_id)
    except Member.DoesNotExist:
        return False
    return EntityMember.objects.filter(member=member.user, role=EntityMember.Role.LEADER).exists()
