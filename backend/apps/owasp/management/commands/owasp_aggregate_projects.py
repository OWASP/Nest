"""A command to update OWASP projects data."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project


class Command(BaseCommand):
    help = "Aggregate OWASP projects data."

    def add_arguments(self, parser):
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *_args, **options):
        active_projects = Project.active_projects.order_by("-created_at")
        active_projects_count = active_projects.count()

        offset = options["offset"]
        projects = []
        for idx, project in enumerate(active_projects[offset:]):
            prefix = f"{idx + offset + 1} of {active_projects_count}"
            print(f"{prefix:<10} {project.owasp_url}")

            # Deactivate project with archived repositories.
            if project.owasp_repository.is_archived:
                project.is_active = False

            project.created_at = project.owasp_repository.created_at

            pushed_at = []
            released_at = []

            commits_count = []
            contributors_count = []
            forks_count = []
            open_issues_count = []
            releases_count = []
            stars_count = []
            subscribers_count = []
            watchers_count = []

            languages = set()
            licenses = set()
            topics = set()

            project.organizations.clear()
            project.owners.clear()
            for repository in project.repositories.all():
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
                commits_count.append(repository.commits_count)
                contributors_count.append(repository.contributors_count)
                forks_count.append(repository.forks_count)
                open_issues_count.append(repository.open_issues_count)
                releases_count.append(repository.releases.count())
                stars_count.append(repository.stars_count)
                subscribers_count.append(repository.subscribers_count)
                watchers_count.append(repository.watchers_count)

                languages.update(repository.top_languages)
                if repository.license:
                    licenses.add(repository.license)
                if repository.topics:
                    topics.update(repository.topics)

            project.pushed_at = max(pushed_at)
            if released_at:
                project.released_at = max(released_at)
            project.updated_at = max(pushed_at + released_at)

            project.commits_count = max(commits_count)
            project.contributors_count = max(contributors_count)
            project.forks_count = max(forks_count)
            project.open_issues_count = max(open_issues_count)
            project.releases_count = max(releases_count)
            project.stars_count = max(stars_count)
            project.subscribers_count = max(subscribers_count)
            project.watchers_count = max(watchers_count)

            project.languages = sorted(languages)
            project.licenses = sorted(licenses)
            project.topics = sorted(topics)

            project.has_active_repositories = project.repositories.filter(
                is_archived=False, is_empty=False
            ).exists()

            projects.append(project)

        # Bulk save data.
        Project.bulk_save(projects)
