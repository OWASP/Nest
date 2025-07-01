import strawberry
from apps.github.graphql.nodes.user import UserNode


@strawberry.type
class MentorNode:
    @strawberry.field
    def login(self) -> str:
        return self.github_user.login

    @strawberry.field
    def name(self) -> str:
        return self.github_user.name

    @strawberry.field
    def avatar_url(self) -> str:
        return self.github_user.avatar_url
