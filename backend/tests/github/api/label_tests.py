import pytest

from apps.github.api.label import LabelSerializer


@pytest.mark.parametrize(
    "label_data",
    [
        {
            "name": "bug",
            "description": "Indicates a bug in the project",
            "color": "f29513",
            "nest_created_at": "2024-12-30T00:00:00Z",
            "nest_updated_at": "2024-12-30T00:00:00Z",
        },
        {
            "name": "enhancement",
            "description": "Indicates a new feature or enhancement",
            "color": "a2eeef",
            "nest_created_at": "2024-12-29T00:00:00Z",
            "nest_updated_at": "2024-12-30T00:00:00Z",
        },
    ],
)
def test_label_serializer(label_data):
    serializer = LabelSerializer(data=label_data)
    assert serializer.is_valid(), serializer.errors
    validated_data = serializer.validated_data
    assert validated_data["name"] == label_data["name"]
    assert validated_data["description"] == label_data["description"]
    assert validated_data["color"] == label_data["color"]
