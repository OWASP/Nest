from unittest.mock import patch

from apps.owasp.index.registry.committee import CommitteeIndex


class TestCommitteeIndex:
    def test_get_entities(self):
        """Test get_entities returns active committees with select_related."""
        with patch.object(CommitteeIndex, "__init__", lambda self: None):
            index = CommitteeIndex()

        with patch("apps.owasp.index.registry.committee.Committee") as mock_committee:
            mock_manager = mock_committee.active_committees
            mock_manager.select_related.return_value = ["committee1", "committee2"]

            result = index.get_entities()

            mock_manager.select_related.assert_called_once_with("owasp_repository")
            assert result == ["committee1", "committee2"]
