"""Management command to populate sample project categories for testing."""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.owasp.models.category import ProjectCategory


class Command(BaseCommand):
    """Populate sample categories with hierarchy."""

    help = "Populate sample project categories with nested subcategories"

    def handle(self, *args, **options):
        """Execute command to create sample categories."""
        self.stdout.write(self.style.SUCCESS("Starting category population..."))

        # Define category hierarchy structure
        categories_data = [
            {
                "name": "Testing",
                "description": "Security testing and quality assurance tools and methodologies",
                "children": [
                    {
                        "name": "Infrastructure Testing",
                        "description": "Infrastructure and deployment testing tools",
                        "children": [
                            {
                                "name": "Kubernetes",
                                "description": "Kubernetes security testing and scanning",
                            },
                            {
                                "name": "Docker",
                                "description": "Container security testing and scanning",
                            },
                        ],
                    },
                    {
                        "name": "Web Application Testing",
                        "description": "Web application security testing tools",
                        "children": [
                            {
                                "name": "Dynamic Analysis",
                                "description": "Dynamic analysis and runtime testing",
                            },
                            {
                                "name": "Static Analysis",
                                "description": "Static code analysis and SAST tools",
                            },
                        ],
                    },
                ],
            },
            {
                "name": "Documentation",
                "description": "Reference materials, guides, and documentation",
                "children": [
                    {
                        "name": "API Documentation",
                        "description": "API documentation and references",
                        "children": [
                            {
                                "name": "REST API",
                                "description": "REST API documentation",
                            },
                        ],
                    },
                    {
                        "name": "Concept Guides",
                        "description": "Educational guides on security concepts",
                    },
                ],
            },
            {
                "name": "Tools & Libraries",
                "description": "Reusable tools, libraries, and frameworks",
                "children": [
                    {
                        "name": "Code Libraries",
                        "description": "Code libraries and SDKs",
                        "children": [
                            {
                                "name": "Python Libraries",
                                "description": "Python security libraries",
                            },
                            {
                                "name": "JavaScript Libraries",
                                "description": "JavaScript security libraries",
                            },
                        ],
                    },
                    {
                        "name": "Command-Line Tools",
                        "description": "CLI tools for security operations",
                    },
                ],
            },
            {
                "name": "Policy & Governance",
                "description": "Policy frameworks and governance guidance",
                "children": [
                    {
                        "name": "Standards",
                        "description": "Security standards and frameworks",
                    },
                ],
            },
        ]

        def create_categories_recursive(parent_data, parent_category=None):
            """Create categories recursively with proper parent relationships."""
            for item in parent_data:
                name = item["name"]
                description = item.get("description", "")
                slug = slugify(name)

                # Check if category already exists
                existing = ProjectCategory.objects.filter(slug=slug).first()
                if existing:
                    self.stdout.write(
                        self.style.WARNING(f"  Category '{name}' already exists - skipping")
                    )
                    category = existing
                else:
                    category = ProjectCategory.objects.create(
                        name=name,
                        slug=slug,
                        description=description,
                        parent=parent_category,
                        is_active=True,
                    )
                    depth = "  "
                    if parent_category:
                        depth = "    " if parent_category.parent else "  "
                    self.stdout.write(
                        self.style.SUCCESS(f"{depth}✓ Created: {category.full_path}")
                    )

                # Recursively create children
                if item.get("children"):
                    create_categories_recursive(item["children"], category)

        # Create all categories
        create_categories_recursive(categories_data)

        self.stdout.write(
            self.style.SUCCESS(
                "\n✓ Category population complete! Categories are ready for filtering."
            )
        )
