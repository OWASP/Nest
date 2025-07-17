from unittest.mock import MagicMock, patch

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.member import MemberSitemap


class TestMemberSitemap:
    @patch("apps.sitemap.views.member.User")
    def test_items(self, mock_user):
        mock_obj = MagicMock(is_indexable=True)
        mock_user.objects.filter.return_value = [mock_obj]
        sitemap = MemberSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        sitemap = MemberSitemap()

        assert sitemap.location(MagicMock(nest_key="bar")) == "/members/bar"

    def test_inherits_from_base(self):
        assert issubclass(MemberSitemap, BaseSitemap)
