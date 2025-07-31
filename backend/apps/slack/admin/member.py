"""Member admin configuration."""

from django.contrib import admin

from apps.slack.models.member import Member

from .mixins import SlackUserRelatedAdminMixin, SuggestedUsersAdminMixin


class MemberAdmin(SlackUserRelatedAdminMixin, SuggestedUsersAdminMixin, admin.ModelAdmin):
    """Admin for Member model."""

    actions = ("approve_suggested_users",)
    autocomplete_fields = ("user",)
    filter_horizontal = ("suggested_users",)
    list_display = ("slack_user_id", "username", "real_name", "is_bot", "workspace")
    list_filter = ("is_bot", "workspace")
    list_select_related = ("user", "workspace")
    ordering = ("-created_at",)
    search_fields = ("slack_user_id", "username", "real_name", "email", "user__login")


admin.site.register(Member, MemberAdmin)
