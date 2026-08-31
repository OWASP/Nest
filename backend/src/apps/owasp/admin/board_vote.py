"""Board vote admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_vote import BoardVote


class BoardVoteAdmin(admin.ModelAdmin):
    """Admin for BoardVote model."""

    filter_horizontal = ("in_favor", "against", "abstain", "recused")
    list_display = ("motion", "result", "type", "tally")
    list_filter = ("result", "type")
    raw_id_fields = ("motion",)
    search_fields = ("motion__title", "tally")


admin.site.register(BoardVote, BoardVoteAdmin)
