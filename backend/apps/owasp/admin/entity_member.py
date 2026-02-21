"""EntityMember admin configuration."""

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project


class EntityMemberAdmin(admin.ModelAdmin):
    """Admin for EntityMember records (generic link to any OWASP entity)."""

    actions = ("approve_members",)
    autocomplete_fields = ("member",)
    list_display = (
        "member_name",
        "member",
        "entity",
        "owasp_url",
        "role",
        "is_active",
        "is_reviewed",
        "order",
    )
    list_filter = (
        "role",
        "is_active",
        "is_reviewed",
    )
    raw_id_fields = ("member",)
    search_fields = (
        "member__login",
        "member__name",
        "description",
    )
    ordering = ("member__name", "order")

    @admin.action(description="Approve selected members")
    def approve_members(self, request, queryset) -> None:
        """Admin action to approve selected members.

        Sets is_active and is_reviewed flags for selected entity members.

        Args:
            request: The HTTP request object.
            queryset: QuerySet of EntityMember instances to approve.

        """
        self.message_user(
            request,
            f"Successfully approved {queryset.update(is_active=True, is_reviewed=True)} members.",
        )

    @admin.display(description="Entity", ordering="entity_type")
    def entity(self, obj) -> str:
        """Display entity as a link in the admin list view.

        Args:
            obj: The EntityMember instance.

        Returns:
            str: HTML link to the entity's admin page or '-' if entity is missing.

        """
        return (
            format_html(
                '<a href="{}" target="_blank">{}</a>',
                reverse(
                    f"admin:{obj.entity_type.app_label}_{obj.entity_type.model}_change",
                    args=[obj.entity_id],
                ),
                obj.entity,
            )
            if obj.entity
            else "-"
        )

    @admin.display(description="OWASP URL", ordering="entity_type")
    def owasp_url(self, obj) -> str:
        """Display entity OWASP website link in admin list view.

        Args:
            obj: The EntityMember instance.

        Returns:
            str: HTML link to the entity's OWASP website or '-' if entity is missing.

        """
        entity = obj.entity
        return (
            format_html('<a href="{}" target="_blank">↗️</a>', entity.owasp_url)
            if entity and hasattr(entity, "owasp_url")
            else "-"
        )

    def get_search_results(self, request, queryset, search_term) -> tuple[models.QuerySet, bool]:
        """Extend search results to include entity name or key matches.

        Searches across Project, Chapter, and Committee entities by name or key
        and includes matching results in the EntityMember search results.

        Args:
            request: The HTTP request object.
            queryset: Initial QuerySet of EntityMember instances.
            search_term: The search term entered by the user.

        Returns:
            tuple: (QuerySet, use_distinct) where QuerySet includes matching members
                   and related entities by name/key, and use_distinct indicates
                   if DISTINCT should be applied to the query.

        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            project_ids = Project.objects.filter(
                Q(name__icontains=search_term) | Q(key__icontains=search_term)
            ).values_list("pk", flat=True)

            chapter_ids = Chapter.objects.filter(
                Q(name__icontains=search_term) | Q(key__icontains=search_term)
            ).values_list("pk", flat=True)

            committee_ids = Committee.objects.filter(
                Q(name__icontains=search_term) | Q(key__icontains=search_term)
            ).values_list("pk", flat=True)

            project_ct = ContentType.objects.get_for_model(Project)
            chapter_ct = ContentType.objects.get_for_model(Chapter)
            committee_ct = ContentType.objects.get_for_model(Committee)

            entity_match_query = (
                Q(entity_type=project_ct, entity_id__in=list(project_ids))
                | Q(entity_type=chapter_ct, entity_id__in=list(chapter_ids))
                | Q(entity_type=committee_ct, entity_id__in=list(committee_ids))
            )

            queryset |= self.model.objects.filter(entity_match_query)
            use_distinct = True

        return queryset, use_distinct


admin.site.register(EntityMember, EntityMemberAdmin)
