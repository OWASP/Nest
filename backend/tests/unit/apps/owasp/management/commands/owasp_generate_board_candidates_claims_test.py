import json
from argparse import ArgumentParser
from unittest.mock import Mock

import pytest
from django.db import IntegrityError

from apps.owasp.management.commands.owasp_generate_board_candidates_claims import Command
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember


class TestGenerateBoardCandidatesClaimsCommand:
    @pytest.fixture
    def command(self, mocker):
        cmd = Command()
        cmd.stdout = Mock()
        cmd.stderr = Mock()
        cmd.style = Mock()
        cmd.style.ERROR = lambda x: x
        cmd.style.SUCCESS = lambda x: x
        cmd.style.WARNING = lambda x: x
        return cmd

    def test_add_arguments(self, command):
        parser = ArgumentParser()
        command.add_arguments(parser)
        args = parser.parse_args(["--source-years", "2022", "2023", "--year", "2024"])
        assert args.source_years == [2022, 2023]
        assert args.year == 2024
        assert not args.dry_run

    def test_get_filename_from_candidate_name(self, command):
        assert command.get_filename_from_candidate_name("John Doe", 2025) == "john_doe.md"
        assert command.get_filename_from_candidate_name("Jane-Smith", 2024) == "jane_smith.md"
        assert command.get_filename_from_candidate_name("Bob", 2022) == "bob_2022.md"

    def test_generate_claims(self, command, mocker):
        mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.OpenAi"
        )
        mock_extract = mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.extract_json_from_markdown"
        )
        mock_extract.return_value = json.dumps(
            [
                {"name": "Claim 1", "description": "Desc 1"},
                {"name": "Claim 2", "description": "Desc 2"},
            ]
        )

        candidate = EntityMember()
        board = BoardOfDirectors()

        claims = command.generate_claims("markdown content", candidate, board)
        assert len(claims) == 2
        assert claims[0].name == "Claim 1"
        assert claims[0].description == "Desc 1"
        assert claims[0].candidate == candidate
        assert claims[0].board == board
        assert claims[0].status == BoardCandidateClaim.Status.DRAFT

    def test_generate_claims_invalid_json(self, command, mocker):
        mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.OpenAi"
        )
        mock_extract = mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.extract_json_from_markdown"
        )
        mock_extract.return_value = "invalid json"

        candidate = EntityMember(member_name="John Doe")
        board = BoardOfDirectors()

        claims = command.generate_claims("markdown content", candidate, board)
        assert claims == []
        command.stderr.write.assert_called()

    def test_generate_claims_not_a_list(self, command, mocker):
        mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.OpenAi"
        )
        mock_extract = mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.extract_json_from_markdown"
        )
        mock_extract.return_value = json.dumps({"name": "Claim 1"})

        candidate = EntityMember(member_name="John Doe")
        board = BoardOfDirectors()

        claims = command.generate_claims("markdown content", candidate, board)
        assert claims == []
        command.stderr.write.assert_called()

    def test_generate_claims_invalid_claim_data(self, command, mocker):
        mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.OpenAi"
        )
        mock_extract = mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.extract_json_from_markdown"
        )
        mock_extract.return_value = json.dumps(
            [
                {"name": "Valid Claim", "description": "Valid desc"},
                "not_a_dict",
                42,
            ]
        )

        candidate = EntityMember()
        board = BoardOfDirectors()

        claims = command.generate_claims("markdown content", candidate, board)
        assert len(claims) == 1
        assert claims[0].name == "Valid Claim"

    def test_generate_claims_empty_name(self, command, mocker):
        mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.OpenAi"
        )
        mock_extract = mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.extract_json_from_markdown"
        )
        mock_extract.return_value = json.dumps(
            [
                {"name": "", "description": "Empty name claim"},
                {"name": "   ", "description": "Whitespace name claim"},
            ]
        )

        candidate = EntityMember()
        board = BoardOfDirectors()

        claims = command.generate_claims("markdown content", candidate, board)
        assert len(claims) == 0

    def test_generate_claims_empty_response(self, command, mocker):
        mock_openai_cls = mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.OpenAi"
        )
        mock_openai_inst = mock_openai_cls.return_value
        mock_openai_inst.set_prompt.return_value = mock_openai_inst
        mock_openai_inst.set_input.return_value = mock_openai_inst
        mock_openai_inst.complete.return_value = ""

        candidate = EntityMember()
        board = BoardOfDirectors()

        claims = command.generate_claims("markdown content", candidate, board)
        assert claims == []

    def test_generate_claims_strips_html(self, command, mocker):
        mock_openai_cls = mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.OpenAi"
        )
        mock_openai_inst = mock_openai_cls.return_value
        mock_openai_inst.set_prompt.return_value = mock_openai_inst
        mock_openai_inst.set_input.return_value = mock_openai_inst
        mock_openai_inst.complete.return_value = json.dumps(
            [{"name": "Test Claim", "description": "Test description"}]
        )

        candidate = EntityMember()
        board = BoardOfDirectors()

        html_content = "<div style='color:red'><p>Hello <b>World</b></p></div>"
        claims = command.generate_claims(html_content, candidate, board)

        actual_input = mock_openai_inst.set_input.call_args[0][0]
        assert "<div" not in actual_input
        assert "<p>" not in actual_input
        assert "<b>" not in actual_input
        assert "Hello World" in actual_input

        assert len(claims) == 1
        assert claims[0].name == "Test Claim"

    @pytest.fixture
    def handle_mocks(self, mocker):
        mocks = {}
        mocks["board_get"] = mocker.patch(
            "apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get"
        )
        mocks["content_type_get"] = mocker.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model"
        )
        mocks["entity_member_filter"] = mocker.patch(
            "apps.owasp.models.entity_member.EntityMember.objects.filter"
        )
        mocks["board_candidate_claim_filter"] = mocker.patch(
            "apps.owasp.models.board_candidate_claim.BoardCandidateClaim.objects.filter"
        )
        mocks["get_repo_file"] = mocker.patch(
            "apps.owasp.management.commands.owasp_generate_board_candidates_claims.get_repository_file_content"
        )
        mocks["generate_claims"] = mocker.patch.object(Command, "generate_claims")
        return mocks

    def test_handle_board_not_found(self, command, handle_mocks):
        handle_mocks["board_get"].side_effect = BoardOfDirectors.DoesNotExist
        command.handle(source_years=[2023], year=2024, name=None, dry_run=False)
        command.stderr.write.assert_called_with("Board of Directors for year 2024 not found.")

    def test_handle_no_candidates(self, command, handle_mocks):
        mock_board = Mock()
        handle_mocks["board_get"].return_value = mock_board

        mock_qs = Mock()
        mock_qs.exists.return_value = False
        if_name_qs = Mock()
        if_name_qs.exists.return_value = False
        mock_qs.filter.return_value = if_name_qs
        handle_mocks["entity_member_filter"].return_value = mock_qs

        command.handle(source_years=[2023], year=2024, name="John Doe", dry_run=False)
        command.stderr.write.assert_called_with("No candidates found matching the criteria.")

    def test_handle_success(self, command, handle_mocks):
        mock_board = Mock()
        mock_board.id = 1
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        mock_claim_qs = Mock()
        mock_claim_qs.exists.return_value = False
        handle_mocks["board_candidate_claim_filter"].return_value = mock_claim_qs

        handle_mocks["get_repo_file"].return_value = "markdown content"

        mock_claim = Mock(spec=BoardCandidateClaim)
        mock_claim.name = "Claim 1"
        mock_claim.description = "Desc 1"
        handle_mocks["generate_claims"].return_value = [mock_claim]

        command.handle(source_years=[2023], year=2024, name=None, dry_run=False)

        mock_claim.save.assert_called_once()
        command.stdout.write.assert_any_call("Saved 1 claims for John Doe")
        command.stdout.write.assert_any_call("Finished generating claims for 1 candidates.")

    def test_handle_dry_run(self, command, handle_mocks):
        mock_board = Mock()
        mock_board.id = 1
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        mock_claim_qs = Mock()
        mock_claim_qs.exists.return_value = False
        handle_mocks["board_candidate_claim_filter"].return_value = mock_claim_qs

        handle_mocks["get_repo_file"].return_value = "markdown content"

        mock_claim = Mock(spec=BoardCandidateClaim)
        mock_claim.name = "Claim 1"
        mock_claim.description = "Desc 1"
        handle_mocks["generate_claims"].return_value = [mock_claim]

        command.handle(source_years=[2023], year=2024, name=None, dry_run=True)

        mock_claim.save.assert_not_called()
        command.stdout.write.assert_any_call("[DRY RUN] Would have saved claims for John Doe")
        command.stdout.write.assert_any_call("[DRY RUN] Finished processing 1 candidates.")

    def test_handle_claims_exist(self, command, handle_mocks):
        mock_board = Mock()
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        mock_claim_qs = Mock()
        mock_claim_qs.exists.return_value = True
        handle_mocks["board_candidate_claim_filter"].return_value = mock_claim_qs

        command.handle(source_years=[2023], year=2024, name=None, dry_run=False)

        command.stdout.write.assert_any_call("Claims already exist for John Doe, skipping...")
        handle_mocks["get_repo_file"].assert_not_called()

    def test_handle_claims_exist_dry_run(self, command, handle_mocks):
        mock_board = Mock()
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        mock_claim_qs = Mock()
        mock_claim_qs.exists.return_value = True
        handle_mocks["board_candidate_claim_filter"].return_value = mock_claim_qs

        handle_mocks["get_repo_file"].return_value = "markdown content"

        mock_claim = Mock(spec=BoardCandidateClaim)
        mock_claim.name = "Claim 1"
        mock_claim.description = "Desc 1"
        handle_mocks["generate_claims"].return_value = [mock_claim]

        command.handle(source_years=[2023], year=2024, name=None, dry_run=True)

        handle_mocks["get_repo_file"].assert_called()
        mock_claim.save.assert_not_called()
        command.stdout.write.assert_any_call("[DRY RUN] Would have saved claims for John Doe")

    def test_handle_no_markdown_content(self, command, handle_mocks):
        mock_board = Mock()
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        mock_claim_qs = Mock()
        mock_claim_qs.exists.return_value = False
        handle_mocks["board_candidate_claim_filter"].return_value = mock_claim_qs

        handle_mocks["get_repo_file"].return_value = "404: Not Found"

        command.handle(source_years=[2023], year=2024, name=None, dry_run=False)

        command.stderr.write.assert_called_with(
            "Could not find any markdown files for John Doe in source years [2023]"
        )

    def test_handle_generate_claims_failed(self, command, handle_mocks):
        mock_board = Mock()
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        mock_claim_qs = Mock()
        mock_claim_qs.exists.return_value = False
        handle_mocks["board_candidate_claim_filter"].return_value = mock_claim_qs

        handle_mocks["get_repo_file"].return_value = "markdown content"

        handle_mocks["generate_claims"].return_value = []

        command.handle(source_years=[2023], year=2024, name=None, dry_run=False)

        command.stderr.write.assert_called_with("Failed to generate claims for John Doe.")

    def test_handle_save_claim_integrity_error(self, command, handle_mocks):
        mock_board = Mock()
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        mock_claim_qs = Mock()
        mock_claim_qs.exists.return_value = False
        handle_mocks["board_candidate_claim_filter"].return_value = mock_claim_qs

        handle_mocks["get_repo_file"].return_value = "markdown content"

        mock_claim = Mock(spec=BoardCandidateClaim)
        mock_claim.name = "Claim 1"
        mock_claim.save.side_effect = IntegrityError("Integrity Error")
        handle_mocks["generate_claims"].return_value = [mock_claim]

        command.handle(source_years=[2023], year=2024, name=None, dry_run=False)

        command.stderr.write.assert_any_call(
            "Failed to save claim 'Claim 1' for John Doe: Integrity Error"
        )

    def test_handle_save_claim_unexpected_error(self, command, handle_mocks):
        mock_board = Mock()
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        mock_claim_qs = Mock()
        mock_claim_qs.exists.return_value = False
        handle_mocks["board_candidate_claim_filter"].return_value = mock_claim_qs

        handle_mocks["get_repo_file"].return_value = "markdown content"

        mock_claim = Mock(spec=BoardCandidateClaim)
        mock_claim.name = "Claim 1"
        mock_claim.save.side_effect = Exception("Unexpected")
        handle_mocks["generate_claims"].return_value = [mock_claim]

        command.handle(source_years=[2023], year=2024, name=None, dry_run=False)

        command.stderr.write.assert_any_call(
            "Unexpected error saving claim 'Claim 1' for John Doe: Unexpected"
        )

    def test_handle_duplicate_claim_names(self, command, handle_mocks):
        mock_board = Mock()
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        mock_claim_qs = Mock()
        mock_claim_qs.exists.return_value = False
        handle_mocks["board_candidate_claim_filter"].return_value = mock_claim_qs

        handle_mocks["get_repo_file"].return_value = "markdown content"

        mock_claim_1 = Mock(spec=BoardCandidateClaim)
        mock_claim_1.name = "Same Claim"
        mock_claim_1.description = "First"
        mock_claim_2 = Mock(spec=BoardCandidateClaim)
        mock_claim_2.name = "Same Claim"
        mock_claim_2.description = "Second"
        handle_mocks["generate_claims"].return_value = [mock_claim_1, mock_claim_2]

        command.handle(source_years=[2023], year=2024, name=None, dry_run=False)

        mock_claim_1.save.assert_called_once()
        mock_claim_2.save.assert_not_called()

    def test_handle_process_candidate_error(self, command, handle_mocks):
        mock_board = Mock()
        handle_mocks["board_get"].return_value = mock_board

        mock_candidate = Mock(spec=EntityMember)
        mock_candidate.member_name = "John Doe"

        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_candidate]))
        handle_mocks["entity_member_filter"].return_value = mock_qs

        handle_mocks["board_candidate_claim_filter"].side_effect = Exception("Processing Error")

        command.handle(source_years=[2023], year=2024, name=None, dry_run=False)

        command.stderr.write.assert_any_call(
            "Failed to process candidate John Doe: Processing Error"
        )
