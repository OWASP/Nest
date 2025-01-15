from unittest.mock import Mock, patch

import pytest

from apps.slack.actions.home import handle_home_actions


class TestHandleHomeActions:
    @pytest.fixture()
    def mock_slack_config(self, mocker):
        mock_app = Mock()
        mocker.patch("apps.slack.apps.SlackConfig.app", mock_app)
        return mock_app

    @pytest.fixture()
    def mock_client(self):
        return Mock()

    @pytest.fixture()
    def mock_ack(self):
        return Mock()

    @pytest.fixture()
    def mock_action_body(self):
        return {
            "user": {"id": "U12345"},
        }

    @pytest.fixture()
    def mock_get_functions(self):
        with (
            patch("apps.owasp.api.search.project.get_projects") as get_projects,
            patch("apps.owasp.api.search.chapter.get_chapters") as get_chapters,
            patch("apps.owasp.api.search.committee.get_committees") as get_committees,
        ):
            yield get_projects, get_chapters, get_committees

    @pytest.fixture(params=["project", "chapter", "committee"])
    def action_type(self, request):
        return request.param

    @pytest.fixture()
    def mock_data(self, action_type):
        data_mapping = {
            "project": {
                "hits": [
                    {
                        "idx_url": "https://example.com/project1",
                        "idx_name": "Project 1",
                        "idx_contributors_count": 10,
                        "idx_forks_count": 5,
                        "idx_stars_count": 100,
                        "idx_summary": "Summary of project 1",
                    }
                ],
                "nbPages": 1,
            },
            "chapter": {
                "hits": [
                    {
                        "idx_url": "https://example.com/chapter1",
                        "idx_name": "Chapter 1",
                        "idx_summary": "Summary of chapter 1",
                    }
                ],
                "nbPages": 1,
            },
            "committee": {
                "hits": [
                    {
                        "idx_url": "https://example.com/committee1",
                        "idx_name": "Committee 1",
                        "idx_summary": "Summary of committee 1",
                    }
                ],
                "nbPages": 1,
            },
        }
        return data_mapping[action_type]

    def test_handle_home_actions(
        self, mock_get_functions, mock_ack, mock_client, mock_action_body, action_type, mock_data
    ):
        get_projects, get_chapters, get_committees = mock_get_functions

        match action_type:
            case "project":
                get_projects.return_value = mock_data
                action_id = "view_projects_action"
                expected_summary = (
                    f"Contributors: {mock_data['hits'][0]['idx_contributors_count']} | "
                    f"Forks: {mock_data['hits'][0]['idx_forks_count']} | "
                    f"Stars: {mock_data['hits'][0]['idx_stars_count']}\n"
                    f"{mock_data['hits'][0]['idx_summary']}"
                )
                expected_url = "*<https://example.com/project1|1. Project 1>*\n"

            case "chapter":
                get_chapters.return_value = mock_data
                action_id = "view_chapters_action"
                expected_summary = f"{mock_data['hits'][0]['idx_summary']}\n"
                expected_url = "*<https://example.com/chapter1|1. Chapter 1>*\n"

            case "committee":
                get_committees.return_value = mock_data
                action_id = "view_committees_action"
                expected_summary = f"{mock_data['hits'][0]['idx_summary']}\n"
                expected_url = "*<https://example.com/committee1|1. Committee 1>*\n"

            case _:
                error_message = "Unknown action_type"
                raise ValueError(error_message)

        body = {
            **mock_action_body,
            "actions": [{"action_id": action_id}],
        }

        handle_home_actions(mock_ack, body, mock_client)

        mock_ack.assert_called_once()

        mock_client.views_publish.assert_called_once_with(
            user_id="U12345",
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Projects", "emoji": True},
                                "value": "view_projects",
                                "action_id": "view_projects_action",
                            },
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Chapters", "emoji": True},
                                "value": "view_chapters",
                                "action_id": "view_chapters_action",
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Committees",
                                    "emoji": True,
                                },
                                "value": "view_committees",
                                "action_id": "view_committees_action",
                            },
                        ],
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{expected_url}{expected_summary}",
                        },
                    },
                ],
            },
        )
