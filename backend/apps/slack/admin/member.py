"""Member admin configuration."""

from django.contrib import admin, messages

from apps.slack.models.member import Member

from .mixins import SlackUserRelatedAdminMixin, SuggestedUsersAdminMixin


class MemberAdmin(admin.ModelAdmin, SlackUserRelatedAdminMixin, SuggestedUsersAdminMixin):
    """Admin for Member model."""

    autocomplete_fields = ("user",)
    list_filter = (
        "is_bot",
        "workspace",
    )
    search_fields = SlackUserRelatedAdminMixin.base_slack_search_fields + (
        "user__login",
    )

admin.site.register(Member, MemberAdmin)
