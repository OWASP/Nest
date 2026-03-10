"""Management command to assign sample categories to projects for testing."""

import random

from django.core.management.base import BaseCommand

from apps.owasp.models.category import ProjectCategory
from apps.owasp.models.project import Project


class Command(BaseCommand):
    """Assign sample categories to existing projects."""

    help = "Assign sample categories to existing projects for testing the filter feature"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Maximum number of projects to assign categories to",
        )

    def handle(self, *args, **options):
        """Execute command to assign categories to projects."""
        self.stdout.write(self.style.SUCCESS("Starting project category assignment..."))

        limit = options["limit"]

        # Get all active categories (don't slice yet to allow re-ordering)
        categories_list = list(ProjectCategory.objects.filter(is_active=True))

        if not categories_list:
            self.stdout.write(
                self.style.ERROR("No categories found. Run 'populate_sample_categories' first.")
            )
            return

        # Get random active projects
        projects = Project.active_projects.all().order_by("?")[:limit]

        if not projects.exists():
            self.stdout.write(self.style.ERROR("No projects found in the database."))
            return

        modified_count = 0

        for project in projects:
            # Assign 1-3 random categories to each project
            # NOSONAR: Using random for test data generation, not security-sensitive
            random_categories = random.sample(categories_list, min(3, len(categories_list)))

            # Add categories to project (avoid duplicates)
            for category in random_categories:
                if not project.categories.filter(id=category.id).exists():
                    project.categories.add(category)
                    modified_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {project.name} assigned to {len(random_categories)} categories"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Category assignment complete! {modified_count} category assignments made."
            )
        )
        self.stdout.write(
            self.style.SUCCESS("You can now test the category filter on the projects page.")
        )
