from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model for GitHub-authenticated users."""
    
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        help_text="Required. 150 characters or fewer. Letters, digits, and @/./+/-/_ only.",
    )
    github_id = models.CharField(
        verbose_name="GitHub ID",
        unique=True
    )
    avatar_url = models.URLField(
        verbose_name="Avatar URL",
        blank=True,
    )
    github_profile = models.URLField(
        verbose_name="GitHub Profile",
        blank=True,
    )
    name = models.CharField(
        verbose_name="Full Name",
        max_length=255,
        blank=True,
    )
    email = models.EmailField(
        verbose_name="Email Address",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "user"
        verbose_name_plural = "users"
        ordering = ["username"]

    def __str__(self) -> str:
        return self.name or self.username