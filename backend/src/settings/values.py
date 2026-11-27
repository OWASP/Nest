"""Custom django-configurations value types."""

from configurations import values


class OptionalSecretValue(values.SecretValue):
    """Read a secret from the environment, defaulting to empty when unset."""

    def __init__(self, *args, **kwargs):
        """Initialize an optional secret that defaults to empty when unset."""
        kwargs.setdefault("default", "")
        kwargs.setdefault("environ", True)
        kwargs["environ_required"] = False
        # Bypass SecretValue.__init__, which rejects defaults and requires the env var.
        super(values.SecretValue, self).__init__(*args, **kwargs)

    def setup(self, name):
        """Resolve the secret value from the environment or return the default."""
        return super(values.SecretValue, self).setup(name)
