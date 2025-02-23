"""OWASP stats GraphQL node."""

import graphene


class StatsNode(graphene.ObjectType):
    """Stats node."""

    active_projects_stats = graphene.Int()
    active_chapters_stats = graphene.Int()
    contributors_stats = graphene.Int()
    countries_stats = graphene.Int()
