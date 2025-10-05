from datetime import datetime

import pytest

from apps.api.rest.v0.member import MemberDetail


class TestMemberSchema:
    @pytest.mark.parametrize(
        "member_data",
        [
            {
                "avatar_url": "https://github.com/images/johndoe.png",
                "bio": "Developer advocate",
                "company": "GitHub",
                "created_at": "2024-12-30T00:00:00Z",
                "email": "john@example.com",
                "followers_count": 10,
                "following_count": 5,
                "location": "San Francisco",
                "login": "johndoe",
                "name": "John Doe",
                "public_repositories_count": 3,
                "title": "Senior Engineer",
                "twitter_username": "johndoe",
                "updated_at": "2024-12-30T00:00:00Z",
                "url": "https://github.com/johndoe",
            },
        ],
    )
    def test_user_schema(self, member_data):
        member = MemberDetail(**member_data)

        assert member.avatar_url == member_data["avatar_url"]
        assert member.bio == member_data["bio"]
        assert member.company == member_data["company"]
        assert member.created_at == datetime.fromisoformat(member_data["created_at"])
        assert member.followers_count == member_data["followers_count"]
        assert member.following_count == member_data["following_count"]
        assert member.location == member_data["location"]
        assert member.login == member_data["login"]
        assert member.name == member_data["name"]
        assert member.public_repositories_count == member_data["public_repositories_count"]
        assert member.title == member_data["title"]
        assert member.twitter_username == member_data["twitter_username"]
        assert member.updated_at == datetime.fromisoformat(member_data["updated_at"])
        assert member.url == member_data["url"]

        assert not hasattr(member, "email")
