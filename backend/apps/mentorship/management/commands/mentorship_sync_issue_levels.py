"""A command to sync issue level with Tasklevel."""

from django.core.management.base import BaseCommand
from django.db.models import Prefetch

from apps.github.models.issue import Issue
from apps.github.models.label import Label
from apps.mentorship.models.task_level import TaskLevel
from apps.mentorship.utils import normalize_name


class Command(BaseCommand):
    """Sync the `level` field on Issues based on matching labels, respecting Module constraints.

    If any label matches a TaskLevel in the Issue's Module, that TaskLevel is assigned.
    """

    help = "Assign a TaskLevel to each Issue by matching labels within the same Module."

    def _build_module_level_maps(self, all_levels):
        """Build a mapping from module ID to a dictionary of data.

        The dictionary contains a 'label_to_level_map' for normalized label/level
        names to TaskLevel objects.
        """
        module_data_map = {}
        for level in all_levels:
            module_id = level.module_id
            level_map_container = module_data_map.setdefault(module_id, {"label_to_level_map": {}})
            level_map = level_map_container["label_to_level_map"]

            normalized_level_name = normalize_name(level.name)
            level_map[normalized_level_name] = level

            for label_name in level.labels:
                normalized_label = normalize_name(label_name)
                level_map[normalized_label] = level
        return module_data_map

    def _find_best_match_level(
        self,
        issue_labels_normalized,
        issue_mentorship_modules,
        module_data_map,
    ):
        """Find the best matching TaskLevel for an issue based on its labels and modules."""
        for module in issue_mentorship_modules:
            if module.id in module_data_map:
                module_level_map = module_data_map[module.id]["label_to_level_map"]
                for label_name in issue_labels_normalized:
                    if label_name in module_level_map:
                        return module_level_map[label_name]
        return None

    def handle(self, *args, **options):
        self.stdout.write("Starting...")

        # 1. Build a per-module map (normalized label → TaskLevel)
        all_levels = TaskLevel.objects.select_related("module").order_by("name")

        if not all_levels.exists():
            self.stdout.write(
                self.style.WARNING("No TaskLevel objects found in the database. Exiting.")
            )
            return

        module_data_map = self._build_module_level_maps(all_levels)
        self.stdout.write(f"Built label maps for {len(module_data_map)} modules.")

        # 2.match issue labels to TaskLevels
        issues_to_update = []
        issues_query = Issue.objects.prefetch_related(
            Prefetch("labels", queryset=Label.objects.only("name")),
            "mentorship_modules",
        ).select_related("level")

        for issue in issues_query:
            issue_labels_normalized = {normalize_name(label.name) for label in issue.labels.all()}

            best_match_level = self._find_best_match_level(
                issue_labels_normalized,
                list(issue.mentorship_modules.all()),
                module_data_map,
            )

            if issue.level != best_match_level:
                issue.level = best_match_level
                issues_to_update.append(issue)

        if issues_to_update:
            updated_count = len(issues_to_update)
            Issue.objects.bulk_update(issues_to_update, ["level"])
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated the level for {updated_count} issues.")
            )
        else:
            self.stdout.write(self.style.SUCCESS("All issue levels are already up-to-date."))
