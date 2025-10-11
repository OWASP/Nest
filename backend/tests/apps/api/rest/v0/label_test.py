import pytest

from apps.api.rest.v0.label import LabelDetail


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
        label = LabelDetail(**label_data)

        assert label.color == label_data["color"]
        assert label.description == label_data["description"]
        assert label.name == label_data["name"]
