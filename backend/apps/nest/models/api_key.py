"""Nest app API key model."""

import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

MAX_ACTIVE_KEYS = 5


class ApiKey(models.Model):
    """API key model."""

    class Meta:
        db_table = "nest_api_keys"
        verbose_name_plural = "API keys"
        ordering = ["-created_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    hash = models.CharField(max_length=64, unique=True)
    is_revoked = models.BooleanField(default=False)
    key_suffix = models.CharField(max_length=4, blank=True)
    name = models.CharField(max_length=100)

    # FKs.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    def __str__(self):
        """Human-readable representation of the API key."""
        return f"{self.name} ({'revoked' if self.is_revoked else 'active'})"

    @classmethod
    def create(cls, user, name, expires_at=None):
        """Create a new API key instance."""
        if cls.active_count_for_user(user) >= MAX_ACTIVE_KEYS:
            return None

        raw_key = cls.generate_raw_key()
        key_hash = cls.generate_hash_key(raw_key)
        instance = cls.objects.create(
            expires_at=expires_at,
            hash=key_hash,
            key_suffix=raw_key[-4:],
            name=name,
            user=user,
        )
        return instance, raw_key

    @classmethod
    def active_count_for_user(cls, user) -> int:
        """Return active API keys for the user."""
        now = timezone.now()
        return (
            cls.objects.filter(
                user=user,
                is_revoked=False,
            )
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
            .count()
        )

    @classmethod
    def authenticate(cls, raw_key: str) -> "ApiKey | None":
        """Authenticate an API key using the raw key."""
        try:
            api_key = cls.objects.get(hash=cls.generate_hash_key(raw_key))
        except cls.DoesNotExist:
            return None

        return api_key if api_key.is_valid() else None

    @staticmethod
    def generate_raw_key():
        """Generate a secure random API key."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_hash_key(raw_key: str) -> str:
        """Generate a SHA-256 hash of the raw API key."""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def is_valid(self):
        """Check if the API key is valid."""
        return not self.is_revoked and (not self.expires_at or self.expires_at > timezone.now())
