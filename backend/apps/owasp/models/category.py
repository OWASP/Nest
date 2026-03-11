"""OWASP app category models."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel


class ProjectCategory(TimestampedModel):
    """Project category model for hierarchical taxonomy.

    Supports up to 3 levels of nesting:
    - Level 1: Category (e.g., "Testing")
    - Level 2: Subcategory (e.g., "Infrastructure Testing")
    - Level 3: Sub-subcategory (e.g., "Kubernetes")
    """

    class Meta:
        """Model options."""

        db_table = "owasp_project_categories"
        indexes = [
            models.Index(fields=["is_active"], name="category_is_active_idx"),
        ]
        verbose_name_plural = "Project categories"
        ordering = ["name"]

    # Fields
    name = models.CharField(
        verbose_name="Name",
        max_length=100,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Slug",
        max_length=100,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Description",
        blank=True,
        default="",
        help_text="Optional description for this category",
    )

    # Hierarchy - parent reference for nested categories (up to 3 levels)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Parent category",
        help_text="Empty for top-level. Set to create subcategories (max 3 levels)",
    )

    is_active = models.BooleanField(
        verbose_name="Is active",
        default=True,
        help_text="Inactive categories won't be used for filtering",
    )

    def __str__(self) -> str:
        """Category human readable representation."""
        return self.name

    @property
    def level(self) -> int:
        """Get the nesting level of this category.

        Returns:
            int: Level 1 for top-level, 2 for subcategory, 3 for sub-subcategory.

        """
        if self.parent is None:
            return 1
        if self.parent.parent is None:
            return 2
        return 3

    @property
    def full_path(self) -> str:
        """Get the full hierarchical path of this category.

        Returns:
            str: Full path like "Testing -> Infrastructure Testing -> Kubernetes"

        """
        parts = [self.name]
        current = self.parent
        while current is not None:
            parts.insert(0, current.name)
            current = current.parent
        return " -> ".join(parts)

    def get_descendants(self) -> models.QuerySet:
        """Get all descendants (children and their children).

        Returns:
            QuerySet: All descendant categories.

        """
        descendants = list(self.children.all())
        for child in self.children.all():
            descendants.extend(child.get_descendants())
        return type(self).objects.filter(id__in=[d.id for d in descendants])

    def get_ancestors(self) -> models.QuerySet:
        """Get all ancestors (parent and grandparent, etc).

        Returns:
            QuerySet: All ancestor categories.

        """
        ancestors: list[ProjectCategory] = []
        current = self.parent
        while current is not None:
            ancestors.insert(0, current)
            current = current.parent
        return type(self).objects.filter(id__in=[a.id for a in ancestors])
