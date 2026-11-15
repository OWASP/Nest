import pytest

from apps.ai.evaluation.datasets.project_fixtures import get_project_fixture


@pytest.mark.parametrize(("case_id", "count"), [("proj-001", 2), ("proj-004", 1)])
def test_project_records_are_independent(case_id, count):
    records = get_project_fixture(case_id)
    original_name = records[0]["idx_name"]
    records[0]["idx_name"] = "Changed by a caller"
    records.append({"idx_name": "Extra"})
    fresh = get_project_fixture(case_id)
    assert len(fresh) == count
    assert fresh[0]["idx_name"] == original_name


def test_unknown_project_fixture_is_rejected():
    with pytest.raises(KeyError):
        get_project_fixture("unknown-case")


def test_flagship_snapshot_identifies_two_official_examples():
    records = get_project_fixture("proj-001")
    assert {record["idx_name"] for record in records} == {
        "OWASP Dependency-Check",
        "OWASP Juice Shop",
    }
    assert all(record["idx_level"] == "flagship" for record in records)
    assert all(record["idx_url"].startswith("https://owasp.org/projects/") for record in records)
