from datetime import datetime

import pytest

from apps.api.rest.v0.member import MemberSchema


class TestMemberSchema:
    @pytest.mark.parametrize(
        "member_data",
        [
            {
                "name": "John Doe",
                "login": "johndoe",
                "company": "GitHub",
                "location": "San Francisco",
                "avatar_url": "https://github.com/images/johndoe.png",
                "bio": "Developer advocate",
                "email": "john@example.com",
                "followers_count": 10,
                "following_count": 5,
                "public_repositories_count": 3,
                "title": "Senior Engineer",
                "twitter_username": "johndoe",
                "url": "https://github.com/johndoe",
                "created_at": "2024-12-30T00:00:00Z",
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_user_schema(self, member_data):
        member = MemberSchema(**member_data)

        assert member.name == member_data["name"]
        assert member.login == member_data["login"]
        assert member.company == member_data["company"]
        assert member.location == member_data["location"]
        assert member.avatar_url == member_data["avatar_url"]
        assert member.bio == member_data["bio"]
        assert member.followers_count == member_data["followers_count"]
        assert member.following_count == member_data["following_count"]
        assert member.public_repositories_count == member_data["public_repositories_count"]
        assert member.title == member_data["title"]
        assert member.twitter_username == member_data["twitter_username"]
        assert member.url == member_data["url"]
        assert member.created_at == datetime.fromisoformat(member_data["created_at"])
        assert member.updated_at == datetime.fromisoformat(member_data["updated_at"])

        assert not hasattr(member, "email")
