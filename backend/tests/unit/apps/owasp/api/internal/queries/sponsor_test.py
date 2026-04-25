from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.sponsor import SponsorQuery
from apps.owasp.models.sponsor import Sponsor


class TestSponsorQuery:
    def test_sponsors_returns_sorted_by_type(self):
        """Test sponsors resolver sorts by sponsor type priority."""
        diamond = MagicMock()
        diamond.sponsor_type = Sponsor.SponsorType.DIAMOND

        silver = MagicMock()
        silver.sponsor_type = Sponsor.SponsorType.SILVER

        platinum = MagicMock()
        platinum.sponsor_type = Sponsor.SponsorType.PLATINUM

        with patch.object(Sponsor.objects, "all", return_value=[silver, diamond, platinum]):
            query = SponsorQuery()
            result = list(query.sponsors())

        assert result[0] == diamond
        assert result[1] == platinum
        assert result[2] == silver
