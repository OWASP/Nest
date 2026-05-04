"""Custom GraphQL context for OWASP Nest."""

from strawberry.django.context import StrawberryDjangoContext

from apps.github.api.internal.dataloaders import make_github_dataloaders


class NestGraphQLContext(StrawberryDjangoContext):
    """Nest GraphQL context."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the context with fresh dataloader instances."""
        super().__init__(*args, **kwargs)
        self.github_dataloaders = make_github_dataloaders()
