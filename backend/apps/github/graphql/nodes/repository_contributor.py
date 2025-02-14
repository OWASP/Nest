"""GitHub repository GraphQL node."""

#!/usr/bin/env python3
import graphene


class RepositoryContributorNode(graphene.ObjectType):
    """Repository contributor node."""

    avatar_url = graphene.String()
    contributions_count = graphene.Int()
    login = graphene.String()
    name = graphene.String()
