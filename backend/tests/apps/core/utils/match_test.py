from apps.core.utils.index import get_params_for_index


class TestParamsMapping:
    def test_get_params_for_issues(self):
        result = get_params_for_index("issues")
        expected = {
            "attributesToHighlight": [],
            "removeWordsIfNoResults": "allOptional",
            "minProximity": 4,
            "typoTolerance": "min",
            "attributesToRetrieve": [
                "idx_comments_count",
                "idx_created_at",
                "idx_hint",
                "idx_labels",
                "idx_project_name",
                "idx_project_url",
                "idx_repository_languages",
                "idx_summary",
                "idx_title",
                "idx_updated_at",
                "idx_url",
            ],
            "distinct": 1,
        }
        assert result == expected

    def test_get_params_for_chapters(self):
        result = get_params_for_index("chapters")
        expected = {
            "attributesToHighlight": [],
            "removeWordsIfNoResults": "allOptional",
            "minProximity": 4,
            "typoTolerance": "min",
            "attributesToRetrieve": [
                "_geoloc",
                "idx_created_at",
                "idx_is_active",
                "idx_key",
                "idx_leaders",
                "idx_name",
                "idx_region",
                "idx_related_urls",
                "idx_suggested_location",
                "idx_summary",
                "idx_tags",
                "idx_top_contributors",
                "idx_updated_at",
                "idx_url",
            ],
            "aroundLatLngViaIP": True,
        }
        assert result == expected

    def test_get_params_for_projects(self):
        result = get_params_for_index("projects")
        expected = {
            "attributesToHighlight": [],
            "removeWordsIfNoResults": "allOptional",
            "minProximity": 4,
            "typoTolerance": "min",
            "attributesToRetrieve": [
                "idx_contributors_count",
                "idx_forks_count",
                "idx_is_active",
                "idx_issues_count",
                "idx_key",
                "idx_languages",
                "idx_leaders",
                "idx_level",
                "idx_name",
                "idx_organizations",
                "idx_repositories_count",
                "idx_repositories",
                "idx_stars_count",
                "idx_summary",
                "idx_top_contributors",
                "idx_topics",
                "idx_type",
                "idx_updated_at",
                "idx_url",
            ],
        }
        assert result == expected

    def test_get_params_for_committees(self):
        result = get_params_for_index("committees")
        expected = {
            "attributesToHighlight": [],
            "removeWordsIfNoResults": "allOptional",
            "minProximity": 4,
            "typoTolerance": "min",
            "attributesToRetrieve": [
                "idx_created_at",
                "idx_key",
                "idx_leaders",
                "idx_name",
                "idx_related_urls",
                "idx_summary",
                "idx_top_contributors",
                "idx_updated_at",
                "idx_url",
            ],
        }
        assert result == expected

    def test_get_params_for_users(self):
        result = get_params_for_index("users")
        expected = {
            "attributesToHighlight": [],
            "removeWordsIfNoResults": "allOptional",
            "minProximity": 4,
            "typoTolerance": "min",
            "attributesToRetrieve": [
                "idx_avatar_url",
                "idx_badge_count",
                "idx_bio",
                "idx_company",
                "idx_created_at",
                "idx_email",
                "idx_followers_count",
                "idx_following_count",
                "idx_key",
                "idx_location",
                "idx_login",
                "idx_name",
                "idx_public_repositories_count",
                "idx_title",
                "idx_updated_at",
                "idx_url",
            ],
        }
        assert result == expected

    def test_get_params_for_unknown_index(self):
        result = get_params_for_index("unknown_index")
        expected = {
            "attributesToHighlight": [],
            "removeWordsIfNoResults": "allOptional",
            "minProximity": 4,
            "typoTolerance": "min",
            "attributesToRetrieve": [],
        }
        assert result == expected
