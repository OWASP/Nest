from apps.ai.evaluation.datasets.dataset import get_case_by_id, get_dataset
from apps.ai.evaluation.datasets.schema import EvalCategory


class TestDataset:
    def test_get_all_cases(self):
        cases = get_dataset()
        assert len(cases) >= 25

    def test_unique_case_ids(self):
        cases = get_dataset()
        ids = [c.id for c in cases]
        assert len(ids) == len(set(ids))

    def test_filter_by_category_enum(self):
        proj_cases = get_dataset(EvalCategory.PROJECT)
        assert len(proj_cases) > 0
        assert all(c.category == EvalCategory.PROJECT for c in proj_cases)

    def test_filter_by_category_str(self):
        gsoc_cases = get_dataset("gsoc")
        assert len(gsoc_cases) > 0
        assert all(c.category == EvalCategory.GSOC for c in gsoc_cases)

    def test_get_case_by_id_found(self):
        case = get_case_by_id("proj-001")
        assert case is not None
        assert case.id == "proj-001"
        assert case.category == EvalCategory.PROJECT

    def test_get_case_by_id_not_found(self):
        case = get_case_by_id("non-existent-id")
        assert case is None

    def test_all_cases_have_valid_fields(self):
        cases = get_dataset()
        for case in cases:
            assert case.id.strip() != ""
            assert case.query.strip() != ""
            assert case.expected_intent.strip() != ""
            assert isinstance(case.category, EvalCategory)
