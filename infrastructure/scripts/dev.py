"""Local development workflows for OWASP Nest."""

from pathlib import Path

from dotenv import load_dotenv

from scripts.localstack import LocalStack


class LocalInfrastructureRunner:
    """Orchestrator for local infrastructure workflows."""

    def __init__(self) -> None:
        """Initialize the local infrastructure runner."""
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(self.env_path)
        self.localstack = LocalStack()

    def start_localstack(self) -> None:
        """Start LocalStack for local development.

        Raises:
            InfrastructureError: If LocalStack fails to start or become ready.

        """
        full_image, _ = self.localstack.image_info(self.root_dir)
        self.localstack.start(full_image)
        self.localstack.wait_ready()

    def stop_localstack(self) -> None:
        """Stop LocalStack for local development.

        Raises:
            InfrastructureError: If LocalStack fails to start or become ready.

        """
        self.localstack.stop()


def main():
    """Bootstrap and run local infrastructure workflows."""
    runner = LocalInfrastructureRunner()
    runner.start_localstack()


if __name__ == "__main__":
    main()
