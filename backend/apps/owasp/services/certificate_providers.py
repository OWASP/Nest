"""Certificate provider classes for Contributor Recognition Program."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from django.conf import settings

from apps.owasp.models.crp.certificate import Certificate

if TYPE_CHECKING:
    from apps.github.models.user import User
    from apps.owasp.models.crp.recognition_enums import TierChoices


class BaseCertificateProvider(ABC):
    """Abstract base class for certificate providers."""

    @abstractmethod
    def issue(self, user: User, score: int, tier: TierChoices) -> None:
        """Issue a certificate.

        Args:
            user (User): The user for whom the certificate is issued.
            score (int): The score when the certificate is issued.
            tier (TierChoices): The tier for which the certificate is issued.

        """


class LocalCertificateProvider(BaseCertificateProvider):
    """Certificate provider that records certificate metadata in local database."""

    def issue(self, user: User, score: int, tier: TierChoices) -> None:
        """Record the certificate metadata in the local database.

        Args:
            user (User): The user for whom the certificate is issued.
            score (int): The score when the certificate is issued.
            tier (TierChoices): The tier for which the certificate is issued.

        """
        Certificate.objects.create(
            github_user=user,
            score=score,
            tier=tier,
        )


class CertificateProviderFactory:
    """Factory for resolving and instantiating certificate providers."""

    PROVIDERS: dict[str, type[BaseCertificateProvider]] = {
        "local": LocalCertificateProvider,
    }

    @classmethod
    def get_provider(cls) -> BaseCertificateProvider:
        """Resolve and instantiate the configured certificate provider.

        Returns:
            BaseCertificateProvider: The active certificate provider instance.

        Raises:
            ValueError: If the configured provider is unknown.

        """
        provider_type = getattr(settings, "CERTIFICATE_PROVIDER", "local")
        provider_class = cls.PROVIDERS.get(provider_type)
        if not provider_class:
            error_msg = f"Unknown certificate provider: {provider_type}"
            raise ValueError(error_msg)

        return provider_class()
