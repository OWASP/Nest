from datetime import datetime

import pytest

from apps.github.api.rest.v1.user import UserSchema


class TestUserSchema:
    @pytest.mark.parametrize(
        "user_data",
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
    def test_user_schema(self, user_data):
        user = UserSchema(**user_data)

        assert user.name == user_data["name"]
        assert user.login == user_data["login"]
        assert user.company == user_data["company"]
        assert user.location == user_data["location"]
        assert user.avatar_url == user_data["avatar_url"]
        assert user.bio == user_data["bio"]
        assert user.email == user_data["email"]
        assert user.followers_count == user_data["followers_count"]
        assert user.following_count == user_data["following_count"]
        assert user.public_repositories_count == user_data["public_repositories_count"]
        assert user.title == user_data["title"]
        assert user.twitter_username == user_data["twitter_username"]
        assert user.url == user_data["url"]
        assert user.created_at == datetime.fromisoformat(user_data["created_at"])
        assert user.updated_at == datetime.fromisoformat(user_data["updated_at"])
