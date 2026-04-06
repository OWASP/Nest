import pytest
from django.core.exceptions import ValidationError

from apps.owasp.models.enums.project import AudienceChoices, validate_audience


class TestAudienceValidator:
    @pytest.mark.parametrize(
        "valid_input",
        [
            [],
            ["builder"],
            ["breaker", "defender"],
            list(AudienceChoices.values),
        ],
    )
    def test_validator_passes_with_valid_input(self, valid_input):
        try:
            validate_audience(valid_input)
        except ValidationError as e:
            pytest.fail(
                f"Validator incorrectly raised an error for valid input {valid_input}: {e}"
            )

    def test_validator_fails_with_non_list_input(self):
        with pytest.raises(ValidationError) as exception_info:
            validate_audience("builder")

        assert exception_info.value.messages == ["Audience must be a list."]

    @pytest.mark.parametrize(
        ("invalid_input", "invalid_keywords"),
        [
            (["hacker"], "['hacker']"),
            (["builder", "tester"], "['tester']"),
            (["breaker", "hacker", "tester"], "['hacker', 'tester']"),
            (["Builder"], "['Builder']"),
        ],
    )
    def test_validator_fails_with_invalid_keywords_in_list(self, invalid_input, invalid_keywords):
        expected_message = f"Invalid audience keywords: {invalid_keywords}"

        with pytest.raises(ValidationError) as exception_info:
            validate_audience(invalid_input)

        assert exception_info.value.messages == [expected_message]
