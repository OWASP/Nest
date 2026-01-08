from apps.owasp.management.commands.owasp_sync_board_candidates import Command


class TestSyncBoardCandidatesCommand:
    def test_get_candidate_name_from_filename(self):
        command = Command()

        assert command.get_candidate_name_from_filename("john-doe.md") == "John Doe"
        assert command.get_candidate_name_from_filename("jane_smith.md") == "Jane Smith"
        assert (
            command.get_candidate_name_from_filename("mary-ann-johnson.md") == "Mary Ann Johnson"
        )

    def test_parse_candidate_metadata_valid(self):
        command = Command()
        content = """---
name: John Doe
email: john.doe@example.com
title: Software Security Professional
---

# Candidate Statement

I am running for the OWASP Board of Directors."""

        metadata = command.parse_candidate_metadata(content)

        assert metadata["name"] == "John Doe"
        assert metadata["email"] == "john.doe@example.com"
        assert metadata["title"] == "Software Security Professional"

    def test_parse_candidate_metadata_no_frontmatter(self):
        command = Command()
        content = "# Just a heading\n\nSome content"

        metadata = command.parse_candidate_metadata(content)

        assert metadata == {}

    def test_parse_candidate_metadata_invalid_yaml(self):
        command = Command()
        content = """---
name: John Doe
invalid: [unclosed
---

Content"""

        metadata = command.parse_candidate_metadata(content)

        assert metadata == {}
