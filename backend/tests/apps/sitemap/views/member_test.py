from unittest.mock import MagicMock, patch

from apps.sitemap.views import MemberSitemap


class TestMemberSitemap:
    @patch("apps.sitemap.views.member.User")
    def test_items(self, mock_user):
        mock_obj = MagicMock(is_indexable=True)
        mock_user.objects.filter.return_value = [mock_obj]
        sitemap = MemberSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        obj = MagicMock()
        obj.get_absolute_url.return_value = "/members/qux"
        sitemap = MemberSitemap()

        assert sitemap.location(obj) == "/members/qux"
