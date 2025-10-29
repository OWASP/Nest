"""Tests for User.chapters property."""

from unittest.mock import Mock, patch

from apps.github.models.user import User


class TestUserChaptersProperty:
    def test_chapters_property_exists(self):
        assert hasattr(User, "chapters")
        assert isinstance(User.chapters, property)

    def test_chapters_returns_filtered_queryset(self):
        user = User(id=1, login="testuser", node_id="U_test123")

        mock_ct_instance = Mock()
        mock_member_qs = Mock()
        mock_member_qs.values_list.return_value = [1, 2, 3]
        mock_chapter_qs = Mock()
        mock_ordered_qs = Mock()
        mock_chapter_qs.order_by.return_value = mock_ordered_qs

        with (
            patch(
                "django.contrib.contenttypes.models.ContentType.objects.get_for_model"
            ) as mock_get_ct,
            patch("apps.owasp.models.entity_member.EntityMember.objects.filter") as mock_em_filter,
            patch("apps.owasp.models.chapter.Chapter.objects.filter") as mock_chapter_filter,
            patch("apps.owasp.models.entity_member.EntityMember.Role") as mock_role,
        ):
            mock_get_ct.return_value = mock_ct_instance
            mock_em_filter.return_value = mock_member_qs
            mock_chapter_filter.return_value = mock_chapter_qs
            mock_role.LEADER = "leader"

            result = user.chapters

            mock_get_ct.assert_called_once()
            mock_em_filter.assert_called_once_with(
                member=user,
                entity_type=mock_ct_instance,
                role="leader",
                is_active=True,
                is_reviewed=True,
            )
            mock_member_qs.values_list.assert_called_once_with("entity_id", flat=True)
            mock_chapter_filter.assert_called_once_with(id__in=[1, 2, 3], is_active=True)
            mock_chapter_qs.order_by.assert_called_once_with("name")
            assert result == mock_ordered_qs

    def test_chapters_filters_by_active(self):
        user = User(id=1, login="testuser", node_id="U_test123")

        mock_member_qs = Mock()
        mock_member_qs.values_list.return_value = []
        mock_chapter_qs = Mock()
        mock_chapter_qs.order_by.return_value = Mock()

        with (
            patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model"),
            patch("apps.owasp.models.entity_member.EntityMember.objects.filter") as mock_em_filter,
            patch("apps.owasp.models.chapter.Chapter.objects.filter") as mock_chapter_filter,
            patch("apps.owasp.models.entity_member.EntityMember.Role") as mock_role,
        ):
            mock_em_filter.return_value = mock_member_qs
            mock_chapter_filter.return_value = mock_chapter_qs
            mock_role.LEADER = "leader"

            _ = user.chapters

            call_kwargs = mock_chapter_filter.call_args[1]
            assert call_kwargs["is_active"] is True

    def test_chapters_ordered_alphabetically(self):
        user = User(id=1, login="testuser", node_id="U_test123")

        mock_member_qs = Mock()
        mock_member_qs.values_list.return_value = []
        mock_chapter_qs = Mock()

        with (
            patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model"),
            patch("apps.owasp.models.entity_member.EntityMember.objects.filter") as mock_em_filter,
            patch("apps.owasp.models.chapter.Chapter.objects.filter") as mock_chapter_filter,
            patch("apps.owasp.models.entity_member.EntityMember.Role") as mock_role,
        ):
            mock_em_filter.return_value = mock_member_qs
            mock_chapter_filter.return_value = mock_chapter_qs
            mock_role.LEADER = "leader"

            _ = user.chapters

            mock_chapter_qs.order_by.assert_called_once_with("name")
