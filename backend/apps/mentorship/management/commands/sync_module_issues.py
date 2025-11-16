"""A command to sync update relation between module and issue and create task."""

from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from github.GithubException import GithubException

from apps.github.auth import get_github_client
from apps.github.models.issue import Issue
from apps.mentorship.models.module import Module
from apps.mentorship.models.task import Task
from apps.mentorship.utils import normalize_name


class Command(BaseCommand):
    """Efficiently syncs issues to mentorship modules based on matching labels."""

    help = (
        "Syncs issues to modules by matching labels from all repositories "
        "associated with the module's project and creates related tasks."
    )
    ALLOWED_GITHUB_HOSTS = {"github.com", "www.github.com"}
    REPO_PATH_PARTS = 2

    def _extract_repo_full_name(self, repository):
        """Extract repository full name from Repository model or URL string."""
        if hasattr(repository, "path"):
            return repository.path

        repo_url = str(repository) if repository else ""
        parsed = urlparse(repo_url)
        if parsed.netloc in self.ALLOWED_GITHUB_HOSTS:
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= self.REPO_PATH_PARTS:
                return "/".join(parts[: self.REPO_PATH_PARTS])
            return None
        return None

    def _get_status(self, issue, assignee):
        """Map GitHub issue state + assignment to task status."""
        if issue.state.lower() == "closed":
            return Task.Status.COMPLETED

        if assignee:
            return Task.Status.IN_PROGRESS

        return Task.Status.TODO

    def _get_last_assigned_date(self, repo, issue_number, assignee_login):
        """Find the most recent 'assigned' event for a specific user using PyGithub."""
        try:
            gh_issue = repo.get_issue(number=issue_number)
            last_dt = None
            for event in gh_issue.get_events():
                if (
                    event.event == "assigned"
                    and event.assignee
                    and event.assignee.login == assignee_login
                ):
                    last_dt = event.created_at

            if last_dt and timezone.is_naive(last_dt):
                return timezone.make_aware(last_dt, timezone.utc)
            return last_dt  # noqa: TRY300

        except GithubException as e:
            self.stderr.write(
                self.style.ERROR(f"Unexpected error for {repo.name}#{issue_number}: {e}")
            )

        return None

    def _build_repo_label_to_issue_map(self):
        """Build a map from (repository_id, normalized_label_name) to a set of issue IDs."""
        self.stdout.write("Building a repository-aware map of labels to issues...")
        repo_label_to_issue_ids = {}
        rows = (
            Issue.objects.filter(labels__isnull=False, repository__isnull=False)
            .values_list("id", "repository_id", "labels__name")
            .iterator(chunk_size=5000)
        )
        for issue_id, repo_id, label_name in rows:
            key = (repo_id, normalize_name(label_name))
            repo_label_to_issue_ids.setdefault(key, set()).add(issue_id)

        self.stdout.write(
            f"Map built. Found issues for {len(repo_label_to_issue_ids)} unique repo-label pairs."
        )
        return repo_label_to_issue_ids

    def _process_module(
        self,
        module,
        repo_label_to_issue_ids,
        gh_client,
        repo_cache,
        verbosity,
    ):
        """Process a single module to link issues and create tasks."""
        project_repos = list(module.project.repositories.all())
        linked_label_names = module.labels
        num_tasks_created = 0

        matched_issue_ids = set()
        for repo in project_repos:
            for label_name in linked_label_names:
                normalized_label = normalize_name(label_name)
                key = (repo.id, normalized_label)
                issues_for_label = repo_label_to_issue_ids.get(key, set())
                matched_issue_ids.update(issues_for_label)

        with transaction.atomic():
            module.issues.set(matched_issue_ids)

            if matched_issue_ids:
                issues = (
                    Issue.objects.filter(
                        id__in=matched_issue_ids,
                        assignees__isnull=False,
                    )
                    .select_related("repository")
                    .prefetch_related("assignees", "labels")
                    .distinct()
                )

                for issue in issues:
                    assignee = issue.assignees.first()
                    if not assignee:
                        continue

                    status = self._get_status(issue, assignee)
                    task, created = Task.objects.get_or_create(
                        issue=issue,
                        assignee=assignee,
                        defaults={"module": module, "status": status},
                    )

                    updates = {}
                    if task.module != module:
                        updates["module"] = module
                    if task.status != status:
                        updates["status"] = status

                    # Only fetch assigned_at when needed.
                    if (created or task.assigned_at is None) and issue.repository:
                        repo_full_name = self._extract_repo_full_name(issue.repository)
                        if repo_full_name:
                            if repo_full_name not in repo_cache:
                                try:
                                    repo_cache[repo_full_name] = gh_client.get_repo(repo_full_name)
                                except GithubException as e:
                                    self.stderr.write(
                                        self.style.ERROR(
                                            f"Failed to fetch repo '{repo_full_name}': {e}"
                                        )
                                    )
                                    repo_cache[repo_full_name] = None
                            repo = repo_cache.get(repo_full_name)
                            if repo:
                                assigned_date = self._get_last_assigned_date(
                                    repo=repo,
                                    issue_number=issue.number,
                                    assignee_login=assignee.login,
                                )
                                if assigned_date:
                                    updates["assigned_at"] = assigned_date
                                    self.stdout.write(
                                        f"Updated assignment date for issue #{issue.number}"
                                    )

                    if created:
                        num_tasks_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Task created for user '{assignee.login}' on issue "
                                f"{issue.repository.name}#{issue.number} "
                                f"in module '{module.name}'"
                            )
                        )

                    if updates:
                        for field, value in updates.items():
                            setattr(task, field, value)
                        task.save(update_fields=list(updates.keys()))

        num_linked = len(matched_issue_ids)
        if num_linked > 0:
            repo_names = ", ".join([r.name for r in project_repos])
            log_message = (
                f"Updated module '{module.name}': set {num_linked} issues from "
                f"repos: [{repo_names}]"
            )
            if num_tasks_created > 0:
                log_message += f" and created {num_tasks_created} tasks."

            self.stdout.write(self.style.SUCCESS(log_message))

            if verbosity > 1 and num_tasks_created > 0:
                self.stdout.write(self.style.SUCCESS(f"  - Created {num_tasks_created} tasks."))
        return num_linked

    def handle(self, *_args, **options):
        self.stdout.write("starting...")
        verbosity = options["verbosity"]
        gh_client = get_github_client()
        repo_cache = {}

        repo_label_to_issue_ids = self._build_repo_label_to_issue_map()

        total_links_created = 0
        total_modules_updated = 0

        self.stdout.write("Processing modules and linking issues...")
        modules_to_process = (
            Module.objects.prefetch_related("project__repositories")
            .exclude(project__repositories__isnull=True)
            .exclude(labels__isnull=True)
            .exclude(labels=[])
        )

        for module in modules_to_process:
            links_created = self._process_module(
                module=module,
                repo_label_to_issue_ids=repo_label_to_issue_ids,
                gh_client=gh_client,
                repo_cache=repo_cache,
                verbosity=verbosity,
            )
            if links_created > 0:
                total_links_created += links_created
                total_modules_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed. {total_links_created} issue links set "
                f"across {total_modules_updated} modules."
            )
        )
