"""Member admin configuration."""

from django.contrib import admin, messages

from apps.slack.models.member import Member


class MemberAdmin(admin.ModelAdmin):
    """Admin for Member model."""

    actions = ("approve_suggested_users",)
    autocomplete_fields = ("user",)
    filter_horizontal = ("suggested_users",)
    list_filter = (
        "is_bot",
        "workspace",
    )
    search_fields = (
        "slack_user_id",
        "username",
        "real_name",
        "email",
        "user__login",
    )

    def approve_suggested_users(self, request, queryset):
        """
        Admin action to assign a suggested user to each selected Member.

        For each Member:
        - If exactly one suggested user exists, it is assigned to the Member.
        - If multiple suggested users exist, an error message is returned because only one can be assigned.
        - If none exist, a warning message is shown.
        
        """
        for entity in queryset:
            suggestions = entity.suggested_users.all()

            if suggestions.count() == 1:
                entity.user = suggestions.first()  # only one suggested user
                entity.save()
                self.message_user(
                    request,
                    f" assigned user for {entity}.",
                    messages.SUCCESS,
                )
            elif suggestions.count() > 1:
                self.message_user(
                    request,
                    f"Error: Multiple suggested users found for {entity}. "
                    f"Only one user can be assigned due to the one-to-one constraint.",
                    messages.ERROR,
                )
            else:
                self.message_user(
                    request,
                    f"No suggested users found for {entity}.",
                    messages.WARNING,
                )

    approve_suggested_users.short_description = "Approve the suggested user (if only one exists)"


admin.site.register(Member, MemberAdmin)
