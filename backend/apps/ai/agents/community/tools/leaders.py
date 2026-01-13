"""Tool for querying entity leaders and member leadership roles."""

from crewai.tools import tool
from django.contrib.contenttypes.models import ContentType

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project


def get_leader_display_name(leader) -> str:
    """Get display name for a leader, preferring real name over username.

    Args:
        leader: EntityMember instance

    Returns:
        Display name (real name with username in parentheses, or just username/name)

    """
    if leader.member:
        # Prefer real name if available
        if (
            leader.member.name
            and leader.member.name.strip()
            and leader.member.name != leader.member.login
        ):
            return f"{leader.member.name} ({leader.member.login})"
        # Fall back to login if no name
        return leader.member.login
    # If no member linked, use member_name from EntityMember
    return leader.member_name


def format_leaders_by_entity(entity, leaders) -> str:
    """Format leaders for a single entity.

    Args:
        entity: The entity (Project, Chapter, or Committee)
        leaders: QuerySet of EntityMember leaders

    Returns:
        Formatted string with entity name and leaders

    """
    entity_name = entity.name or entity.key
    entity_type = entity.__class__.__name__.lower()

    if not leaders.exists():
        return f"*{entity_name}* ({entity_type})\n\nNo leaders are currently listed."

    leaders_list = []
    for leader in leaders:
        leader_name = get_leader_display_name(leader)
        leaders_list.append(leader_name)

    leaders_str = ", ".join(leaders_list)

    return f"👥 *{entity_name}* ({entity_type.title()})\n\nLeaders: {leaders_str}"


def format_entities_by_member(member_name: str, entities_list: list) -> str:
    """Format entities that a member leads.

    Args:
        member_name: Name of the member
        entities_list: List of tuples (entity, entity_type_name)

    Returns:
        Formatted string with member name and entities they lead

    """
    if not entities_list:
        return f"*{member_name}*\n\nThis member does not currently lead any OWASP entities."

    formatted = f"👥 *{member_name}* leads:\n\n"

    for entity, entity_type in entities_list:
        entity_name = entity.name or entity.key
        formatted += f"• *{entity_name}* ({entity_type})\n"

    return formatted


@tool("Get entity leaders or find entities that a member leads")
def get_entity_leaders(entity_name: str | None = None, member_name: str | None = None) -> str:
    """Get leaders for an entity or find entities that a member leads.

    This tool can work in two modes:
    1. Find leaders by entity name: Returns leaders for a specific project,
       chapter, or committee
    2. Find entities by member name: Returns all entities (projects, chapters,
       committees) that a person leads

    Use this tool when users ask about:
    - Who are the leaders of [project/chapter/committee name]?
    - Who leads [entity name]?
    - What does [person name] lead?
    - What entities is [person] a leader of?
    - Project/chapter/committee leadership
    - Community member leadership roles

    Args:
        entity_name: Optional name of the entity (project, chapter, or committee)
            to get leaders for. If provided, returns leaders for that entity.
        member_name: Optional name of the member to find leadership roles for.
            If provided, returns all entities that this member leads.

    Returns:
        Formatted string with leader information or entity leadership information

    Note:
        At least one of entity_name or member_name must be provided.
        If both are provided, entity_name takes precedence.

    """
    if not entity_name and not member_name:
        return (
            "Please provide either:\n"
            "- An entity name (project, chapter, or committee) to find its leaders, or\n"
            "- A member name to find what entities they lead."
        )

    # Mode 1: Find leaders by entity name
    if entity_name:
        entity_name = entity_name.strip()

        # Try to find the entity across Project, Chapter, and Committee
        entity = None
        entity_type_name = None

        # Search in projects
        try:
            entity = Project.objects.get(name__iexact=entity_name, is_active=True)
            entity_type_name = "project"
        except Project.DoesNotExist:
            try:
                # Try by key
                key = entity_name.lower()
                if not key.startswith("www-project-"):
                    key = f"www-project-{key}"
                entity = Project.objects.get(key__iexact=key, is_active=True)
                entity_type_name = "project"
            except Project.DoesNotExist:
                pass

        # Search in chapters if not found
        if not entity:
            try:
                entity = Chapter.objects.get(name__iexact=entity_name, is_active=True)
                entity_type_name = "chapter"
            except Chapter.DoesNotExist:
                try:
                    key = entity_name.lower()
                    if not key.startswith("www-chapter-"):
                        key = f"www-chapter-{key}"
                    entity = Chapter.objects.get(key__iexact=key, is_active=True)
                    entity_type_name = "chapter"
                except Chapter.DoesNotExist:
                    pass

        # Search in committees if not found
        if not entity:
            try:
                entity = Committee.objects.get(name__iexact=entity_name, is_active=True)
                entity_type_name = "committee"
            except Committee.DoesNotExist:
                try:
                    key = entity_name.lower()
                    if not key.startswith("www-committee-"):
                        key = f"www-committee-{key}"
                    entity = Committee.objects.get(key__iexact=key, is_active=True)
                    entity_type_name = "committee"
                except Committee.DoesNotExist:
                    pass

        if not entity:
            return (
                f"No active entity found with name '{entity_name}'. "
                "Please check the name and try again."
            )

        # Get leaders for this entity
        entity_type = ContentType.objects.get_for_model(entity.__class__)
        leaders = EntityMember.objects.filter(
            entity_type=entity_type,
            entity_id=entity.id,
            role=EntityMember.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        ).order_by("order")

        return format_leaders_by_entity(entity, leaders)

    # Mode 2: Find entities by member name
    if member_name:
        member_name = member_name.strip()

        # Search for EntityMember records where this person is a leader
        # Try matching by member_name (case-insensitive partial match)
        leader_members = EntityMember.objects.filter(
            role=EntityMember.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        ).filter(member_name__icontains=member_name)

        # Also try matching by GitHub user login if member is linked
        from apps.github.models.user import User

        try:
            github_user = User.objects.get(login__iexact=member_name)
            leader_members = leader_members | EntityMember.objects.filter(
                role=EntityMember.Role.LEADER,
                is_active=True,
                is_reviewed=True,
                member=github_user,
            )
        except User.DoesNotExist:
            pass

        if not leader_members.exists():
            return (
                f"No leadership roles found for '{member_name}'. "
                "This person may not be a leader of any OWASP entities."
            )

        # Get the actual member name for display (prefer real name)
        display_member_name = member_name
        # Try to find a linked User to get the real name
        for leader_member in leader_members[:1]:  # Just check first one
            if leader_member.member:
                if leader_member.member.name and leader_member.member.name.strip():
                    display_member_name = leader_member.member.name
                    if leader_member.member.name != leader_member.member.login:
                        display_member_name = (
                            f"{leader_member.member.name} ({leader_member.member.login})"
                        )
                else:
                    display_member_name = leader_member.member.login
                break

        # Group by entity
        entities_list = []
        seen_entities = set()

        for leader_member in leader_members:
            entity = leader_member.entity
            if entity and entity.id not in seen_entities:
                # Determine entity type
                entity_type_name = entity.__class__.__name__.lower()
                entities_list.append((entity, entity_type_name))
                seen_entities.add(entity.id)

        return format_entities_by_member(display_member_name, entities_list)

    return "Please provide either an entity name or a member name."
