"""Assert provider version pins are consistent across infrastructure modules."""

from __future__ import annotations

from pathlib import Path

import pytest

INFRASTRUCTURE_ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ("aws", "random")


class TestProviderVersionPins:
    """Checks that aws/random ``required_providers`` pins match across modules."""

    @staticmethod
    def collect_provider_pins(root: Path, provider: str) -> dict[str, set[str]]:
        """Map each ``version`` pin for ``provider`` to the ``main.tf`` paths that use it.

        Args:
            root: Infrastructure directory to scan for ``main.tf`` files.
            provider: Provider local name (for example ``aws`` or ``random``).

        Returns:
            Mapping of version constraint string to relative ``main.tf`` paths.

        """
        pins: dict[str, set[str]] = {}
        provider_header = f"{provider} ="

        for main_tf in sorted(root.rglob("main.tf")):
            if ".terraform" in main_tf.parts:
                continue

            in_provider_block = False
            depth = 0

            for line in main_tf.read_text().splitlines():
                stripped = line.strip()
                if not in_provider_block:
                    if stripped.startswith(provider_header) and "{" in stripped:
                        in_provider_block = True
                        depth = stripped.count("{") - stripped.count("}")
                    continue

                depth += stripped.count("{") - stripped.count("}")
                if stripped.startswith("version") and "=" in stripped:
                    rhs = stripped.split("=", maxsplit=1)[1].strip()
                    # Drop HCL inline comments before reading the quoted pin.
                    for marker in ("#", "//"):
                        if marker in rhs:
                            rhs = rhs.split(marker, maxsplit=1)[0].strip()
                    version = rhs.strip('"').strip("'")
                    relative = str(main_tf.relative_to(root))
                    pins.setdefault(version, set()).add(relative)

                if depth <= 0:
                    in_provider_block = False

        return pins

    @pytest.mark.parametrize("provider", PROVIDERS)
    def test_provider_version_pins_are_consistent(self, provider: str) -> None:
        """Fail when Dependabot (or a manual edit) leaves mismatched provider pins."""
        pins = self.collect_provider_pins(INFRASTRUCTURE_ROOT, provider)
        assert pins, f"no {provider} version pins under {INFRASTRUCTURE_ROOT}"

        if len(pins) > 1:
            details = "\n".join(
                f"  {version}: {', '.join(sorted(files))}"
                for version, files in sorted(pins.items())
            )
            pytest.fail(f"{provider} version pins differ:\n{details}")
