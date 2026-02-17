"""API key model."""

import hashlib
import secrets
import uuid

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

API_KEY_LENGTH = 32
MAX_ACTIVE_KEYS = 3
MAX_WORD_LENGTH = 100


class ApiKey(models.Model):
    """API key model."""

    class Meta:
        """Model options."""

        db_table = "api_keys"
        verbose_name_plural = "API keys"
        ordering = ["-created_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    hash = models.CharField(max_length=64, unique=True)
    is_revoked = models.BooleanField(default=False)
    last_used_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=MAX_WORD_LENGTH)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    # FKs.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    def __str__(self):
        """Human-readable representation of the API key."""
        return f"{self.name} ({'revoked' if self.is_revoked else 'active'})"

    @property
    def is_expired(self):
        """Check if the API key has expired."""
        return self.expires_at < timezone.now()

    @property
    def is_valid(self):
        """Check if the API key is valid."""
        return not self.is_revoked and not self.is_expired

    @classmethod
    @transaction.atomic
    def create(cls, user, name, expires_at):
        """Create a new API key instance."""
        type(user).objects.select_for_update().get(pk=user.pk)

        if user.active_api_keys.count() >= MAX_ACTIVE_KEYS:
            return None

        raw_key = cls.generate_raw_key()
        key_hash = cls.generate_hash_key(raw_key)

        instance = cls.objects.create(
            expires_at=expires_at,
            hash=key_hash,
            name=name,
            user=user,
        )
        return instance, raw_key

    @classmethod
    def authenticate(cls, raw_key: str) -> "ApiKey | None":
        """Authenticate an API key using the raw key."""
        try:
            api_key = cls.objects.get(hash=cls.generate_hash_key(raw_key))
        except cls.DoesNotExist:
            return None

        if api_key.is_valid:
            cls.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())
            return api_key

        return None

    @staticmethod
    def generate_hash_key(raw_key: str) -> str:
        """Generate a SHA-256 hash of the raw API key."""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    @staticmethod
    def generate_raw_key():
        """Generate a secure random API key."""
        return secrets.token_urlsafe(API_KEY_LENGTH)
