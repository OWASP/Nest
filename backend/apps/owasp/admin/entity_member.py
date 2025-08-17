"""EntityMember admin configuration."""

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
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
    fields = (
        "entity_type",
        "entity_id",
        "member",
        "role",
        "order",
        "is_active",
        "is_reviewed",
        "description",
    )
    list_display = (
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
    def approve_members(self, request, queryset):
        """Approve selected members."""
        self.message_user(
            request,
            f"Successfully approved {queryset.update(is_active=True, is_reviewed=True)} members.",
        )

    @admin.display(description="Entity", ordering="entity_type")
    def entity(self, obj):
        """Return entity link."""
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
    def owasp_url(self, obj):
        """Return entity OWASP site URL."""
        return (
            format_html('<a href="{}" target="_blank">↗️</a>', obj.entity.owasp_url)
            if obj.entity
            else "-"
        )

    def get_search_results(self, request, queryset, search_term):
        """Get search results from entity name or key."""
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
