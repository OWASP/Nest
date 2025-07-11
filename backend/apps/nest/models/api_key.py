"""Nest app API key model."""

import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


class APIKey(models.Model):
    """API key model."""

    hash = models.CharField(max_length=64, unique=True)
    key_suffix = models.CharField(max_length=4, blank=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    is_revoked = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_keys", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "nest_api_keys"
        verbose_name_plural = "APIKeys"
        ordering = ["-created_at"]

    @staticmethod
    def generate_raw_key():
        """Generate a secure random API key."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_hash_key(raw_key: str) -> str:
        """Generate a SHA-256 hash of the raw API key."""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    @classmethod
    def create(cls, user, name, expires_at=None):
        """Create a new API key instance."""
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
    def authenticate(cls, raw_key: str):
        """Authenticate an API key using the raw key."""
        key_hash = cls.generate_hash_key(raw_key)
        try:
            api_key = cls.objects.get(hash=key_hash)
            if api_key.is_valid():
                return api_key
        except cls.DoesNotExist:
            return None

    def is_valid(self):
        """Check if the API key is valid."""
        return not self.is_revoked and (not self.expires_at or timezone.now() < self.expires_at)

    def __str__(self):
        """Human-readable representation of the API key."""
        return f"{self.name} ({'revoked' if self.is_revoked else 'active'})"
