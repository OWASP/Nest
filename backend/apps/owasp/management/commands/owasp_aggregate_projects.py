"""A command to update OWASP projects data."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project


class Command(BaseCommand):
    help = "Aggregate OWASP projects data."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *_args, **options) -> None:
        """Handle the command execution."""
        active_projects = Project.active_projects.order_by("-created_at")
        active_projects_count = active_projects.count()

        offset = options["offset"]
        projects = []
        for idx, project in enumerate(active_projects[offset:]):
            prefix = f"{idx + offset + 1} of {active_projects_count}"
            self.stdout.write(f"{prefix:<10} {project.owasp_url}\n")

            # Deactivate project with archived repositories.
            if project.owasp_repository.is_archived:
                project.is_active = False

            project.created_at = project.owasp_repository.created_at

            pushed_at = []
            released_at = []

            commits_count = 0
            contributors_count = 0
            forks_count = 0
            open_issues_count = 0
            releases_count = 0
            stars_count = 0
            subscribers_count = 0
            watchers_count = 0

            languages = set()
            licenses = set()
            topics = set()

            project.organizations.clear()
            project.owners.clear()
            for repository in project.repositories.filter(
                is_empty=False,
                is_fork=False,
                is_template=False,
            ):
                # Update organizations/owners.
                if repository.organization:
                    project.organizations.add(repository.organization)
                project.owners.add(repository.owner)

                # Pushed at.
                pushed_at.append(repository.pushed_at)

                # Released at.
                if repository.latest_release is not None:
                    released_at.append(repository.latest_release.published_at)

                # Counters.
                commits_count += repository.commits_count
                contributors_count += repository.contributors_count
                forks_count += repository.forks_count
                open_issues_count += repository.open_issues_count
                releases_count += repository.releases.count()
                stars_count += repository.stars_count
                subscribers_count += repository.subscribers_count
                watchers_count += repository.watchers_count

                languages.update(repository.top_languages)
                if repository.license:
                    licenses.add(repository.license)
                if repository.topics:
                    topics.update(repository.topics)

            project.pushed_at = max(pushed_at)
            if released_at:
                project.released_at = max(released_at)
            project.updated_at = max(pushed_at + released_at)

            project.commits_count = commits_count
            project.contributors_count = contributors_count
            project.forks_count = forks_count
            project.open_issues_count = open_issues_count
            project.releases_count = releases_count
            project.stars_count = stars_count
            project.subscribers_count = subscribers_count
            project.watchers_count = watchers_count

            project.languages = sorted(languages)
            project.licenses = sorted(licenses)
            project.topics = sorted(topics)

            project.has_active_repositories = project.repositories.filter(
                is_archived=False,
                is_empty=False,
                is_fork=False,
                is_template=False,
            ).exists()

            projects.append(project)

        # Bulk save data.
        Project.bulk_save(projects)
