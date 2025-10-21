"""Tests for MemberSnapshot admin."""

from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.member_snapshot import MemberSnapshotAdmin
from apps.owasp.models.member_snapshot import MemberSnapshot


class TestMemberSnapshotAdmin:
    def test_list_display(self):
        admin = MemberSnapshotAdmin(MemberSnapshot, AdminSite())

        expected_fields = (
            "github_user",
            "start_at",
            "end_at",
            "commits_count",
            "pull_requests_count",
            "issues_count",
            "messages_count",
            "total_contributions",
            "nest_created_at",
        )

        assert admin.list_display == expected_fields

    def test_list_filter(self):
        admin = MemberSnapshotAdmin(MemberSnapshot, AdminSite())

        expected_filters = (
            "start_at",
            "end_at",
            "nest_created_at",
        )

        assert admin.list_filter == expected_filters

    def test_search_fields(self):
        admin = MemberSnapshotAdmin(MemberSnapshot, AdminSite())

        expected_search = (
            "github_user__login",
            "github_user__name",
        )

        assert admin.search_fields == expected_search

    def test_readonly_fields(self):
        admin = MemberSnapshotAdmin(MemberSnapshot, AdminSite())

        expected_readonly = (
            "commits_count",
            "pull_requests_count",
            "issues_count",
            "messages_count",
            "total_contributions",
            "contribution_heatmap_data",
            "communication_heatmap_data",
            "chapter_contributions",
            "project_contributions",
            "repository_contributions",
            "channel_communications",
            "nest_created_at",
            "nest_updated_at",
        )

        assert admin.readonly_fields == expected_readonly

    def test_autocomplete_fields(self):
        admin = MemberSnapshotAdmin(MemberSnapshot, AdminSite())

        expected_autocomplete = (
            "github_user",
            "commits",
            "pull_requests",
            "issues",
            "messages",
        )

        assert admin.autocomplete_fields == expected_autocomplete

    def test_date_hierarchy(self):
        admin = MemberSnapshotAdmin(MemberSnapshot, AdminSite())

        assert admin.date_hierarchy == "start_at"

    def test_has_fieldsets(self):
        admin = MemberSnapshotAdmin(MemberSnapshot, AdminSite())

        assert admin.fieldsets is not None
        assert len(admin.fieldsets) == 5

        assert admin.fieldsets[0][0] == "Snapshot Information"
        assert admin.fieldsets[1][0] == "GitHub Contributions"
        assert admin.fieldsets[2][0] == "Slack Communications"
        assert admin.fieldsets[3][0] == "Statistics"
        assert admin.fieldsets[4][0] == "Timestamps"
