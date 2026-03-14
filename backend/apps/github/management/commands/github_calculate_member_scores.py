"""A command to calculate member ranking scores."""

import logging
from collections import defaultdict
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Q, Sum

from apps.common.models import BATCH_SIZE
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User
from apps.github.services.score import calculate_member_score
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Calculate composite ranking scores for OWASP community members."""

    help = "Calculate composite ranking scores for members"

    def add_arguments(self, parser):
        """Add command-line arguments.

        Args:
            parser: The argument parser instance.

        """
        parser.add_argument(
            "--user",
            type=str,
            help="Specific user login to process",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        user_login = options.get("user")

        if user_login:
            users = User.objects.filter(login=user_login)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f"Member '{user_login}' not found"))
                return
        else:
            users = User.objects.all()

        total_users = users.count()
        self.stdout.write(f"Calculating scores for {total_users} members...")

        owasp_repo_filter = Q(repository__is_fork=True) | Q(
            repository__organization__is_owasp_related_organization=False
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

        user_pr_flags = set(
            User.objects.filter(created_pull_requests__isnull=False)
            .values_list("id", flat=True)
            .distinct()
        )

        user_issue_flags = set(
            User.objects.filter(created_issues__isnull=False)
            .values_list("id", flat=True)
            .distinct()
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

        updated_users = []
        for idx, user in enumerate(users.iterator(chunk_size=BATCH_SIZE)):
            repo_item = repo_data_map.get(user.id, {})
            leadership_info = leadership_data.get(user.id, {})

            user.calculated_score = calculate_member_score(
                contributions_count=repo_item.get("total_contributions", 0),
                distinct_repository_count=repo_item.get("repo_count", 0),
                release_count=user_release_counts.get(user.id, 0),
                chapter_leader_count=leadership_info.get("chapter_leader", 0),
                project_leader_count=leadership_info.get("project_leader", 0),
                committee_member_count=leadership_info.get("committee_member", 0),
                is_board_member=user.id in board_members,
                is_gsoc_mentor=user.id in gsoc_mentors,
                is_owasp_staff=user.is_owasp_staff,
                has_pull_requests=user.id in user_pr_flags,
                has_issues=user.id in user_issue_flags,
                has_releases=user.id in user_release_counts,
                has_contributions=repo_item.get("total_contributions", 0) > 0,
                contribution_data=user.contribution_data,
            )
            updated_users.append(user)

            if len(updated_users) >= BATCH_SIZE:
                User.bulk_save(updated_users, fields=("calculated_score",))
                self.stdout.write(f"  Processed {idx + 1} of {total_users}")
                updated_users = []

        User.bulk_save(updated_users, fields=("calculated_score",))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully calculated scores for {total_users} members")
        )

    @staticmethod
    def _get_leadership_data() -> dict:
        """Aggregate leadership role counts per user.

        Returns:
            dict: Mapping of user_id -> {role_key: count}.

        """
        chapter_ct_id = ContentType.objects.get_for_model(Chapter).id
        project_ct_id = ContentType.objects.get_for_model(Project).id
        committee_ct_id = ContentType.objects.get_for_model(Committee).id

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
            entity_type_id = item["entity_type_id"]
            role = item["role"]
            count = item["count"]
            user_id = item["member_id"]

            if entity_type_id == project_ct_id and role == EntityMember.Role.LEADER:
                result[user_id]["project_leader"] = (
                    result[user_id].get("project_leader", 0) + count
                )
            elif entity_type_id == chapter_ct_id and role == EntityMember.Role.LEADER:
                result[user_id]["chapter_leader"] = (
                    result[user_id].get("chapter_leader", 0) + count
                )
            elif entity_type_id == committee_ct_id:
                result[user_id]["committee_member"] = (
                    result[user_id].get("committee_member", 0) + count
                )

        return dict(result)
