from apps.slack.blocks import divider, get_header, get_pagination_buttons, markdown

EXPECTED_ELEMENT_COUNT = 4
EXPECTED_BUTTON_COUNT = 2


class TestBlocks:
    def test_divider(self):
        divider_block = divider()
        assert divider_block["type"] == "divider"

    def test_markdown(self):
        text = "Test *markdown* text"
        md_block = markdown(text)
        assert md_block["type"] == "section"
        assert md_block["text"]["type"] == "mrkdwn"
        assert md_block["text"]["text"] == text

    def test_get_header(self):
        header_blocks = get_header()
        assert len(header_blocks) == 1
        assert header_blocks[0]["type"] == "actions"

        elements = header_blocks[0]["elements"]
        assert len(elements) == EXPECTED_ELEMENT_COUNT

        action_ids = [element["action_id"] for element in elements]
        expected_actions = [
            "view_projects_action",
            "view_chapters_action",
            "view_committees_action",
            "view_contribute_action",
        ]
        for action in expected_actions:
            assert action in action_ids

    def test_pagination_buttons_first_page(self):
        buttons = get_pagination_buttons("test", 1, 5)
        assert len(buttons) == 1
        assert buttons[0]["text"]["text"] == "Next"
        assert buttons[0]["action_id"] == "view_test_action_next"
        assert buttons[0]["value"] == "2"

    def test_pagination_buttons_middle_page(self):
        buttons = get_pagination_buttons("test", 3, 5)
        assert len(buttons) == EXPECTED_BUTTON_COUNT
        assert buttons[0]["text"]["text"] == "Previous"
        assert buttons[0]["action_id"] == "view_test_action_prev"
        assert buttons[0]["value"] == "2"
        assert buttons[1]["text"]["text"] == "Next"
        assert buttons[1]["action_id"] == "view_test_action_next"
        assert buttons[1]["value"] == "4"

    def test_pagination_buttons_last_page(self):
        buttons = get_pagination_buttons("test", 5, 5)
        assert len(buttons) == 1
        assert buttons[0]["text"]["text"] == "Previous"
        assert buttons[0]["action_id"] == "view_test_action_prev"
        assert buttons[0]["value"] == "4"

    def test_pagination_buttons_single_page(self):
        buttons = get_pagination_buttons("test", 1, 0)
        assert buttons == []

    def test_pagination_buttons_invalid_page(self):
        buttons = get_pagination_buttons("test", 10, 5)
        assert len(buttons) == 1
        assert buttons[0]["text"]["text"] == "Previous"
