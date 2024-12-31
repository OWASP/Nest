import pytest

from apps.github.api.label import LabelSerializer


class TestLabelSerializer:
    @pytest.mark.parametrize(
        "label_data",
        [
            {
                "name": "bug",
                "description": "Indicates a bug in the project",
                "color": "f29513",
            },
            {
                "name": "enhancement",
                "description": "Indicates a new feature or enhancement",
                "color": "a2eeef",
            },
        ],
    )
    def test_label_serializer(self, label_data):
        serializer = LabelSerializer(data=label_data)
        assert serializer.is_valid(), serializer.errors
        validated_data = serializer.validated_data
        assert validated_data["name"] == label_data["name"]
        assert validated_data["description"] == label_data["description"]
        assert validated_data["color"] == label_data["color"]
