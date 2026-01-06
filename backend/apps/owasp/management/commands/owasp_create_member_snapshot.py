"""A command to create member snapshots for a specific user."""

import logging
from collections import defaultdict
from datetime import UTC, datetime , timedelta

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.github.models.commit import Commit
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.member_profile import MemberProfile
from apps.owasp.models.member_snapshot import MemberSnapshot
from apps.owasp.models.project import Project
from apps.slack.models.message import Message

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to create a member snapshot for a specific user."""

    help = "Create a member snapshot for a specific user with their contributions"

    def add_arguments(self, parser):
        """Add command-line arguments.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "username",
            type=str,
            help="GitHub username to create snapshot for",
        )
        parser.add_argument(
            "--start-at",
            type=str,
            help="Start date (YYYY-MM-DD). Defaults to  365 days ago.",
        )
        parser.add_argument(
            "--end-at",
            type=str,
            help="End date (YYYY-MM-DD). Defaults to today.",
        )

    def parse_date(self, date_str: str | None, default: datetime) -> datetime:
        """Parse date string or return default.

        Args:
            date_str (str | None): Date string in YYYY-MM-DD format.
            default (datetime): Default datetime to use if date_str is None.

        Returns:
            datetime: Parsed datetime or default.

        Raises:
            ValueError: If date string format is invalid.

        """
        if not date_str:
            return default

        try:
            return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            error_msg = f"Invalid date format: {date_str}. Use YYYY-MM-DD."
            self.stderr.write(self.style.ERROR(error_msg))
            raise

    def generate_heatmap_data(self, commits, pull_requests, issues, start_at, end_at) -> dict:
        """Generate heatmap data from contributions within the date range.

        Args:
            commits: Queryset or iterable of Commit objects.
            pull_requests: Queryset or iterable of PullRequest objects.
            issues: Queryset or iterable of Issue objects.
            start_at: Start date of the snapshot period.
            end_at: End date of the snapshot period.

        Returns:
            dict: Mapping of date strings (YYYY-MM-DD) to contribution counts.

        """
        from datetime import timedelta

        # Initialize all dates in range with 0
        heatmap_data: dict[str, int] = {}
        current_date = start_at.date()
        end_date = end_at.date()
        while current_date <= end_date:
            heatmap_data[current_date.isoformat()] = 0
            current_date += timedelta(days=1)

        # Count contributions
        for commit in commits:
            if start_at <= commit.created_at <= end_at:
                date_key = commit.created_at.date().isoformat()
                heatmap_data[date_key] += 1

        for pr in pull_requests:
            if start_at <= pr.created_at <= end_at:
                date_key = pr.created_at.date().isoformat()
                heatmap_data[date_key] += 1

        for issue in issues:
            if start_at <= issue.created_at <= end_at:
                date_key = issue.created_at.date().isoformat()
                heatmap_data[date_key] += 1

        return heatmap_data

    def generate_entity_contributions(
        self, user, commits, pull_requests, issues, entity_type: str, start_at, end_at
    ) -> dict:
        """Generate contribution counts per chapter or project led by the user.

        Args:
            user: User instance to get led entities for.
            commits: Queryset or iterable of Commit objects.
            pull_requests: Queryset or iterable of PullRequest objects.
            issues: Queryset or iterable of Issue objects.
            entity_type: Either "chapter" or "project".
            start_at: Start date of the snapshot period.
            end_at: End date of the snapshot period.

        Returns:
            dict: Mapping of entity keys to contribution counts (including 0 for no contributions).

        """
        # Get entities where the user is a leader
        entity_model = Project if entity_type == "project" else Chapter
        content_type = ContentType.objects.get_for_model(entity_model)
        led_entity_ids = EntityMember.objects.filter(
            member=user,
            entity_type=content_type,
            role=EntityMember.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        ).values_list("entity_id", flat=True)

        # Initialize all led entities with 0 contributions
        entity_contributions: dict[str, int] = {}
        if entity_type == "project":
            led_projects = Project.objects.filter(id__in=led_entity_ids, is_active=True)
            for project in led_projects:
                entity_contributions[project.nest_key] = 0
        else:  # chapter
            led_chapters = Chapter.objects.filter(id__in=led_entity_ids, is_active=True)
            for chapter in led_chapters:
                entity_contributions[chapter.nest_key] = 0

        # Get all unique repository IDs from contributions
        repository_ids = set()
        for commit in commits.select_related("repository"):
            repository_ids.add(commit.repository_id)
        for pr in pull_requests.select_related("repository"):
            repository_ids.add(pr.repository_id)
        for issue in issues.select_related("repository"):
            repository_ids.add(issue.repository_id)

        # Build a mapping of repository_id -> entity key (only for led entities)
        # Use nest_key (without www- prefix) to match GraphQL API format
        repo_to_entity: dict[int, str] = {}
        if entity_type == "project":
            # Projects have a M2M 'repositories' field
            projects = Project.objects.filter(
                id__in=led_entity_ids,
                is_active=True,
            ).prefetch_related("repositories")
            for project in projects:
                for repo in project.repositories.all():
                    repo_to_entity[repo.id] = project.nest_key
        else:  # chapter
            # Chapters have a single FK 'owasp_repository' field
            chapters = Chapter.objects.filter(
                id__in=led_entity_ids,
                is_active=True,
            ).select_related("owasp_repository")
            for chapter in chapters:
                if chapter.owasp_repository_id:
                    repo_to_entity[chapter.owasp_repository_id] = chapter.nest_key

        # Count commits (only within date range)
        for commit in commits:
            if commit.created_at and start_at <= commit.created_at <= end_at:
                entity_key = repo_to_entity.get(commit.repository_id)
                if entity_key:
                    entity_contributions[entity_key] += 1

        # Count pull requests (only within date range)
        for pr in pull_requests:
            if pr.created_at and start_at <= pr.created_at <= end_at:
                entity_key = repo_to_entity.get(pr.repository_id)
                if entity_key:
                    entity_contributions[entity_key] += 1

        # Count issues (only within date range)
        for issue in issues:
            if issue.created_at and start_at <= issue.created_at <= end_at:
                entity_key = repo_to_entity.get(issue.repository_id)
                if entity_key:
                    entity_contributions[entity_key] += 1

        return dict(entity_contributions)

    def generate_repository_contributions(self, commits, start_at, end_at) -> dict:
        """Generate top 5 repositories by commit count within date range.

        Args:
            commits: Queryset or iterable of Commit objects.
            start_at: Start date of the snapshot period.
            end_at: End date of the snapshot period.

        Returns:
            dict: Mapping of repository full names to commit counts (top 5).

        """
        repository_counts: dict[str, int] = defaultdict(int)

        # Count commits per repository (only within date range)
        for commit in commits:
            if commit.created_at and start_at <= commit.created_at <= end_at and commit.repository:
                repo_full_name = f"{commit.repository.owner.login}/{commit.repository.name}"
                repository_counts[repo_full_name] += 1

        # Sort by count and take top 5
        sorted_repos = sorted(
            repository_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return dict(sorted_repos)

    def generate_communication_heatmap_data(self, messages, start_at, end_at) -> dict:
        """Generate communication heatmap data from public Slack channels within date range.

        Args:
            messages: Queryset or iterable of Message objects.
            start_at: Start date of the snapshot period.
            end_at: End date of the snapshot period.

        Returns:
            dict: Mapping of date strings (YYYY-MM-DD) to message counts (all dates initialized).

        """
        from datetime import timedelta

        # Initialize all dates in range with 0
        heatmap_data: dict[str, int] = {}
        current_date = start_at.date()
        end_date = end_at.date()
        while current_date <= end_date:
            heatmap_data[current_date.isoformat()] = 0
            current_date += timedelta(days=1)

        # Count messages
        for message in messages:
            if (
                message.created_at
                and start_at <= message.created_at <= end_at
                and message.conversation
                and message.conversation.is_channel
                and not message.conversation.is_private
            ):
                date_key = message.created_at.date().isoformat()
                heatmap_data[date_key] += 1

        return heatmap_data

    def generate_channel_communications(self, messages, start_at, end_at) -> dict:
        """Generate top 5 public channels by message count within date range.

        Args:
            messages: Queryset or iterable of Message objects.
            start_at: Start date of the snapshot period.
            end_at: End date of the snapshot period.

        Returns:
            dict: Mapping of channel names to message counts (top 5).

        """
        channel_counts: dict[str, int] = defaultdict(int)

        # Count messages per public channel (only within date range)
        for message in messages:
            if (
                message.created_at
                and start_at <= message.created_at <= end_at
                and message.conversation
                and message.conversation.is_channel
                and not message.conversation.is_private
            ):
                channel_name = message.conversation.name
                if channel_name:
                    channel_counts[channel_name] += 1

        # Sort by message count and take top 5
        sorted_channels = sorted(
            channel_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return dict(sorted_channels)

    def handle(self, *args, **options):
        """Handle command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        username = options["username"]

        # Default to last 365 days
        default_end = datetime.now(UTC)
        default_start = default_end - timedelta(days=365)

        end_at = self.parse_date(options.get("end_at"), default_end)
        start_at = self.parse_date(options.get("start_at"), default_start)

        self.stdout.write(f"Creating snapshot for user: {username}")
        self.stdout.write(f"Period: {start_at.date()} to {end_at.date()}")
        logger.info(
            "Creating snapshot for %s from %s to %s",
            username,
            start_at.date(),
            end_at.date(),
        )

        # Get user
        try:
            user = User.objects.get(login=username)
        except User.DoesNotExist:
            error_msg = f"User '{username}' not found in database"
            self.stderr.write(self.style.ERROR(error_msg))
            logger.exception("User %s not found", username)
            return

        # Check if snapshot already exists
        existing_snapshot = MemberSnapshot.objects.filter(
            github_user=user,
            start_at=start_at,
            end_at=end_at,
        ).first()

        if existing_snapshot:
            self.stdout.write(
                self.style.WARNING(
                    f"Snapshot already exists for this period (ID: {existing_snapshot.id})"
                )
            )
            self.stdout.write("Updating existing snapshot...")
            snapshot = existing_snapshot
            # Clear existing relationships
            snapshot.commits.clear()
            snapshot.pull_requests.clear()
            snapshot.issues.clear()
            snapshot.messages.clear()
            logger.info("Updating existing snapshot %s", snapshot.id)
        else:
            # Create new snapshot
            snapshot = MemberSnapshot.objects.create(
                github_user=user,
                start_at=start_at,
                end_at=end_at,
            )
            self.stdout.write(f"Created new snapshot (ID: {snapshot.id})")
            logger.info("Created new snapshot %s", snapshot.id)

        # Fetch and link commits
        commits = Commit.objects.filter(
            author=user,
            created_at__gte=start_at,
            created_at__lte=end_at,
        )
        commits_count = commits.count()
        self.stdout.write(f"  Found {commits_count} commit(s) in date range")
        if commits_count > 0:
            snapshot.commits.add(*commits)
            self.stdout.write(f"  Linked {commits_count} commit(s)")
            logger.info("Linked %s commits to snapshot", commits_count)

        # Fetch and link pull requests
        pull_requests = PullRequest.objects.filter(
            author=user,
            created_at__gte=start_at,
            created_at__lte=end_at,
        )
        prs_count = pull_requests.count()
        self.stdout.write(f"  Found {prs_count} pull request(s) in date range")
        if prs_count > 0:
            snapshot.pull_requests.add(*pull_requests)
            self.stdout.write(f"  Linked {prs_count} pull request(s)")
            logger.info("Linked %s pull requests to snapshot", prs_count)

        # Fetch and link issues
        issues = Issue.objects.filter(
            author=user,
            created_at__gte=start_at,
            created_at__lte=end_at,
        )
        issues_count = issues.count()
        self.stdout.write(f"  Found {issues_count} issue(s) in date range")
        if issues_count > 0:
            snapshot.issues.add(*issues)
            self.stdout.write(f"  Linked {issues_count} issue(s)")
            logger.info("Linked %s issues to snapshot", issues_count)

        # Fetch and link Slack messages (if user has Slack profile)
        messages_count = 0
        messages = Message.objects.none()
        try:
            profile = MemberProfile.objects.get(github_user=user)
            if profile.owasp_slack_id:
                messages = Message.objects.filter(
                    author__slack_user_id=profile.owasp_slack_id,
                    created_at__gte=start_at,
                    created_at__lte=end_at,
                ).select_related("conversation")
                messages_count = messages.count()
                if messages_count > 0:
                    snapshot.messages.add(*messages)
                    self.stdout.write(f"  Linked {messages_count} Slack message(s)")
                    logger.info("Linked %s Slack messages to snapshot", messages_count)
            else:
                self.stdout.write("  No Slack ID found in member profile")
                logger.info("No Slack ID found for user %s", username)
        except MemberProfile.DoesNotExist:
            self.stdout.write("  No member profile found (skipping Slack messages)")
            logger.info("No member profile found for user %s", username)

        # Generate heatmap data
        heatmap_data = self.generate_heatmap_data(commits, pull_requests, issues, start_at, end_at)
        snapshot.contribution_heatmap_data = heatmap_data

        # Generate chapter contributions (only for chapters led by the user)
        chapter_contributions = self.generate_entity_contributions(
            user, commits, pull_requests, issues, "chapter", start_at, end_at
        )
        snapshot.chapter_contributions = chapter_contributions

        # Generate project contributions (only for projects led by the user)
        project_contributions = self.generate_entity_contributions(
            user, commits, pull_requests, issues, "project", start_at, end_at
        )
        snapshot.project_contributions = project_contributions

        # Generate repository contributions (top 5 repos by commit count)
        repository_contributions = self.generate_repository_contributions(
            commits, start_at, end_at
        )
        snapshot.repository_contributions = repository_contributions

        # Generate communication heatmap (always, even if no messages to show all dates with 0)
        communication_heatmap = self.generate_communication_heatmap_data(
            messages, start_at, end_at
        )
        snapshot.communication_heatmap_data = communication_heatmap

        # Generate top channels (only if messages exist)
        if messages_count > 0:
            channel_communications = self.generate_channel_communications(
                messages, start_at, end_at
            )
            snapshot.channel_communications = channel_communications

        snapshot.save()

        if heatmap_data:
            self.stdout.write(f"  Generated heatmap data for {len(heatmap_data)} day(s)")
            logger.info("Generated heatmap data for %s days", len(heatmap_data))

        if chapter_contributions:
            self.stdout.write(
                f"  Generated chapter contributions for {len(chapter_contributions)} chapter(s)"
            )
            logger.info("Generated contributions for %s chapters", len(chapter_contributions))

        if project_contributions:
            self.stdout.write(
                f"  Generated project contributions for {len(project_contributions)} project(s)"
            )
            logger.info("Generated contributions for %s projects", len(project_contributions))

        if repository_contributions:
            repo_count = len(repository_contributions)
            self.stdout.write(
                f"  Generated repository contributions for {repo_count} repository(ies)"
            )
            logger.info("Generated contributions for %s repositories", repo_count)

        if communication_heatmap:
            heatmap_days = len(communication_heatmap)
            self.stdout.write(f"  Generated communication heatmap data for {heatmap_days} day(s)")
            logger.info("Generated communication heatmap for %s days", heatmap_days)

        if messages_count and channel_communications:
            channel_count = len(channel_communications)
            self.stdout.write(f"  Generated channel communications for {channel_count} channel(s)")
            logger.info("Generated channel communications for %s channels", channel_count)

        # Summary
        total = snapshot.total_contributions
        if total > 0 or messages_count > 0:
            summary_parts = [
                f"{commits_count} commits",
                f"{prs_count} PRs",
                f"{issues_count} issues",
            ]
            if messages_count > 0:
                summary_parts.append(f"{messages_count} Slack messages")

            # Verify counts from snapshot
            actual_commits = snapshot.commits_count
            actual_prs = snapshot.pull_requests_count
            actual_issues = snapshot.issues_count
            actual_messages = snapshot.messages_count

            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSnapshot created successfully for {username}!\n"
                    f"Total GitHub contributions: {total}\n"
                    f"Details: {', '.join(summary_parts)}\n"
                    f"\nVerification (actual counts in snapshot):\n"
                    f"  Commits: {actual_commits}\n"
                    f"  Pull Requests: {actual_prs}\n"
                    f"  Issues: {actual_issues}\n"
                    f"  Slack Messages: {actual_messages}\n"
                    f"  Total (GitHub only): {actual_commits + actual_prs + actual_issues}"
                )
            )
            logger.info(
                "Snapshot completed: %s total contributions for %s",
                total,
                username,
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"\nSnapshot created but no contributions found for {username} "
                    f"in the period {start_at.date()} to {end_at.date()}"
                )
            )
            logger.warning(
                "No contributions found for %s in period %s to %s",
                username,
                start_at.date(),
                end_at.date(),
            )
