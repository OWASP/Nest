"""GitHub app User model admin."""

from django.contrib import admin

from apps.github.models.user import User
from apps.owasp.models.member_profile import MemberProfile


class MemberProfileInline(admin.StackedInline):
    """MemberProfile inline for User admin."""

    model = MemberProfile
    can_delete = False
    verbose_name_plural = "OWASP Member Profile"
    fields = ("owasp_slack_id", "first_contribution_at")
    readonly_fields = ("first_contribution_at",)


class UserAdmin(admin.ModelAdmin):
    """Admin for User model."""

    inlines = (MemberProfileInline,)
    list_display = (
        "title",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "login",
        "name",
    )


admin.site.register(User, UserAdmin)
