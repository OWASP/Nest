import pytest

from apps.api.rest.v0.label import LabelSchema


class TestLabelSchema:
    @pytest.mark.parametrize(
        "label_data",
        [
            {
                "color": "f29513",
                "description": "Indicates a bug in the project",
                "name": "bug",
            },
            {
                "color": "a2eeef",
                "description": "Indicates a new feature or enhancement",
                "name": "enhancement",
            },
        ],
    )
    def test_label_schema(self, label_data):
        label = LabelSchema(**label_data)
        assert label.name == label_data["name"]
        assert label.description == label_data["description"]
        assert label.color == label_data["color"]
