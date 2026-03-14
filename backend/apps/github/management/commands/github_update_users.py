"""A command to update GitHub users."""

import logging
from collections import defaultdict

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Q, Sum

from apps.common.models import BATCH_SIZE
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User
from apps.github.scoring import calculate_member_score
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update GitHub users."

    def add_arguments(self, parser):
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options):
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        active_users = User.objects.order_by("-created_at")
        active_users_count = active_users.count()
        offset = options["offset"]

        non_indexable_logins = User.get_non_indexable_logins()
        owasp_repo_filter = (
            Q(repository__is_fork=True)
            | Q(repository__organization__is_owasp_related_organization=False)
            | Q(user__login__in=non_indexable_logins)
        )

        repo_data = (
            RepositoryContributor.objects.exclude(owasp_repo_filter)
            .values("user_id")
            .annotate(
                total_contributions=Sum("contributions_count"),
                repo_count=models.Count("repository", distinct=True),
            )
        )
        repo_data_map = {item["user_id"]: item for item in repo_data}

        user_release_counts = dict(
            User.objects.filter(created_releases__isnull=False)
            .annotate(release_count=models.Count("created_releases"))
            .values_list("id", "release_count")
        )

        leadership_data = self._get_leadership_data()

        board_members = set(
            User.objects.filter(
                owasp_profile__is_owasp_board_member=True,
            ).values_list("id", flat=True)
        )
        gsoc_mentors = set(
            User.objects.filter(
                owasp_profile__is_gsoc_mentor=True,
            ).values_list("id", flat=True)
        )

        users = []
        for idx, user in enumerate(active_users[offset:].iterator()):
            prefix = f"{idx + 1} of {active_users_count - offset}"
            self.stdout.write(f"{prefix:<10} {user.title}\n")

            repo_item = repo_data_map.get(user.id, {})
            user.contributions_count = repo_item.get("total_contributions", 0)

            leadership_id = leadership_data.get(user.id, {})
            user.calculated_score = calculate_member_score(
                contributions_count=user.contributions_count,
                distinct_repository_count=repo_item.get("repo_count", 0),
                distinct_project_count=0,
                release_count=user_release_counts.get(user.id, 0),
                chapter_leader_count=leadership_id.get("chapter_leader", 0),
                project_leader_count=leadership_id.get("project_leader", 0),
                committee_member_count=leadership_id.get("committee_member", 0),
                is_board_member=user.id in board_members,
                is_gsoc_mentor=user.id in gsoc_mentors,
                contribution_data=user.contribution_data,
            )
            users.append(user)

            if not len(users) % BATCH_SIZE:
                User.bulk_save(list(users), fields=("contributions_count", "calculated_score"))
                users.clear()

        if users:
            User.bulk_save(list(users), fields=("contributions_count", "calculated_score"))

    @staticmethod
    def _get_leadership_data() -> dict:
        """Aggregate leadership role counts per user.

        Returns:
            dict: Mapping of user_id -> {role_key: count}.

        """
        entity_type_map = {
            ContentType.objects.get_for_model(Chapter).id: "chapter_leader",
            ContentType.objects.get_for_model(Project).id: "project_leader",
            ContentType.objects.get_for_model(Committee).id: "committee_member",
        }

        memberships = (
            EntityMember.objects.filter(
                member__isnull=False,
                is_active=True,
                is_reviewed=True,
                role__in=(EntityMember.Role.LEADER, EntityMember.Role.MEMBER),
            )
            .values("member_id", "entity_type_id", "role")
            .annotate(count=models.Count("id"))
        )

        result: dict = defaultdict(dict)
        for item in memberships:
            role_key = entity_type_map.get(item["entity_type_id"])
            if not role_key:
                continue
            if role_key == "committee_member" or item["role"] == EntityMember.Role.LEADER:
                result[item["member_id"]][role_key] = (
                    result[item["member_id"]].get(role_key, 0) + item["count"]
                )

        return dict(result)
