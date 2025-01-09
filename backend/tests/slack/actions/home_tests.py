import pytest
from unittest.mock import Mock, patch
from apps.slack.actions.home import handle_home_actions


@pytest.fixture()
def mock_slack_config(mocker):
    mock_app = Mock()
    mocker.patch("apps.slack.apps.SlackConfig.app", mock_app)
    return mock_app


@pytest.fixture()
def mock_client():
    return Mock()


@pytest.fixture()
def mock_ack():
    return Mock()


@pytest.fixture()
def mock_action_body():
    return {
        "user": {"id": "U12345"},
    }


@pytest.fixture()
def mock_get_functions(mocker):
    with patch("apps.owasp.api.search.project.get_projects") as get_projects, \
            patch("apps.owasp.api.search.chapter.get_chapters") as get_chapters, \
            patch("apps.owasp.api.search.committee.get_committees") as get_committees:
        yield get_projects, get_chapters, get_committees


@pytest.fixture(params=["project", "chapter", "committee"])
def action_type(request):
    return request.param


@pytest.fixture()
def mock_data(action_type):
    if action_type == "project":
        return {
            "hits": [
                {
                    "idx_url": "https://example.com/project1",
                    "idx_name": "Project 1",
                    "idx_contributors_count": 10,
                    "idx_forks_count": 5,
                    "idx_stars_count": 100,
                    "idx_summary": "Summary of project 1",
                }
            ]
        }
    elif action_type == "chapter":
        return {
            "hits": [
                {
                    "idx_url": "https://example.com/chapter1",
                    "idx_name": "Chapter 1",
                    "idx_summary": "Summary of chapter 1",
                }
            ]
        }
    elif action_type == "committee":
        return {
            "hits": [
                {
                    "idx_url": "https://example.com/committee1",
                    "idx_name": "Committee 1",
                    "idx_summary": "Summary of committee 1",
                }
            ]
        }


def test_handle_home_actions(mock_get_functions, mock_ack, mock_client, mock_action_body, action_type, mock_data):
    get_projects, get_chapters, get_committees = mock_get_functions

    if action_type == "project":
        get_projects.return_value = mock_data
        action_id = 'view_projects_action'
        expected_summary = f"Contributors: {mock_data['hits'][0]['idx_contributors_count']} | Forks: {mock_data['hits'][0]['idx_forks_count']} | Stars: {mock_data['hits'][0]['idx_stars_count']}\n{mock_data['hits'][0]['idx_summary']}"
        expected_url = f"*<https://example.com/project1|1. Project 1>*\n"
    elif action_type == "chapter":
        get_chapters.return_value = mock_data
        action_id = 'view_chapters_action'
        expected_summary = f"{mock_data['hits'][0]['idx_summary']}\n"
        expected_url = f"*<https://example.com/chapter1|1. Chapter 1>*\n"
    elif action_type == "committee":
        get_committees.return_value = mock_data
        action_id = 'view_committees_action'
        expected_summary = f"{mock_data['hits'][0]['idx_summary']}\n"
        expected_url = f"*<https://example.com/committee1|1. Committee 1>*\n"

    body = {
        **mock_action_body,
        "actions": [{"action_id": action_id}],
    }

    handle_home_actions(mock_ack, body, mock_client)

    # Ensure ack was called
    mock_ack.assert_called_once()

    # Check the correct `views_publish` call
    mock_client.views_publish.assert_called_once_with(
        user_id="U12345",
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "actions",
                    "elements": [
                        {"type": "button",
                         "text": {"type": "plain_text", "text": "Projects", "emoji": True},
                         "value": "view_projects",
                         "action_id": 'view_projects_action'},
                        {"type": "button",
                         "text": {"type": "plain_text", "text": "Chapters", "emoji": True},
                         "value": 'view_chapters',
                         "action_id": 'view_chapters_action'},
                        {"type": "button",
                         "text": {"type": "plain_text", "text": 'Committees', 'emoji': True},
                         'value': 'view_committees',
                         'action_id': 'view_committees_action'},
                    ],
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"{expected_url}{expected_summary}",
                    },
                },
            ],
        },
    )
