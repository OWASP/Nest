from django.contrib import admin

from apps.nest.models.sponsorship import Sponsorship


class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ("issue", "price_usd", "slack_user_id")
    search_fields = ("issue__title", "slack_user_id")


admin.site.register(Sponsorship, SponsorshipAdmin)
