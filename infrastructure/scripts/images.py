"""ECR image management and orchestration."""

from pathlib import Path

from scripts.commands import CommandRunner
from scripts.constants import LIVE_DIR, SOURCE_REPO_DIR
from scripts.errors import RunnerError
from scripts.localstack import LocalStack

IMAGE_CONFIG = {
    "backend": {"target": "backend", "buildargs": None},
    "frontend": {"target": None, "buildargs": {"ENV_FILE": ".env.localstack"}},
}


class ImageManager:
    """ECR image manager."""

    def __init__(
        self,
        root_dir: Path | None = None,
        *,
        commands: CommandRunner | None = None,
        localstack: LocalStack | None = None,
    ) -> None:
        """Initialize the ECR image manager.

        Args:
            root_dir (Path, optional): The root directory of the project.
            commands (CommandRunner, optional): Command runner instance.
            localstack (LocalStack, optional): LocalStack manager instance.

        """
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent.parent
        self.commands = commands or CommandRunner()
        self.localstack = localstack or LocalStack(self.commands)

    def build(self, service: str, tag: str) -> None:
        """Build the Docker image for a service.

        Args:
            service (str): The service name (must be a key of IMAGE_CONFIG).
            tag (str): The tag to apply to the built image.

        Raises:
            RunnerError: If docker build exits with a non-zero status.

        """
        self.commands.require("docker")
        config = IMAGE_CONFIG[service]
        args = [
            "buildx",
            "build",
            "--load",
            "--file",
            str(SOURCE_REPO_DIR / "docker" / service / "Dockerfile"),
            "--tag",
            f"{self.repository_url(service)}:{tag}",
        ]
        if config["target"] is not None:
            args += ["--target", config["target"]]
        for key, value in (config["buildargs"] or {}).items():
            args += ["--build-arg", f"{key}={value}"]
        args.append(str(SOURCE_REPO_DIR / service))

        result = self.commands.run("docker", *args)
        if result.returncode != 0:
            message = f"docker build failed for {service}"
            raise RunnerError(message)

    def login(self) -> None:
        """Authenticate the Docker CLI against ECR.

        Raises:
            RunnerError: If awslocal or docker login fails.

        """
        self.commands.require("awslocal")
        self.commands.require("docker")

        password_result = self.commands.run(
            "awslocal",
            "ecr",
            "get-login-password",
            capture_output=True,
        )
        if password_result.returncode != 0:
            message = (
                "awslocal ecr get-login-password failed "
                f"(rc={password_result.returncode}): "
                f"stdout={password_result.stdout!r} stderr={password_result.stderr!r}"
            )
            raise RunnerError(message)

        login_result = self.commands.run(
            "docker",
            "login",
            "--username",
            "AWS",
            "--password-stdin",
            self.registry_url(),
            capture_output=True,
            stdin_input=password_result.stdout,
        )
        if login_result.returncode != 0:
            message = f"docker login failed: {login_result.stderr}"
            raise RunnerError(message)

    def push(self, service: str, tag: str) -> None:
        """Push the tagged image for a service to ECR.

        Args:
            service (str): The service name.
            tag (str): The tag to push.

        Raises:
            RunnerError: If docker push exits with a non-zero status.

        """
        self.commands.require("docker")
        result = self.commands.run(
            "docker",
            "push",
            f"{self.repository_url(service)}:{tag}",
        )
        if result.returncode != 0:
            message = f"docker push failed for {service}"
            raise RunnerError(message)

    def registry_url(self) -> str:
        """Return the ECR registry host shared by all service repositories.

        Returns:
            str: The ECR registry host (e.g. "<account>.dkr.ecr.<region>...").

        Raises:
            RunnerError: If the underlying Terraform output command fails.

        """
        # Any service's repository URL yields the same registry host.
        any_service = next(iter(IMAGE_CONFIG))
        return self.repository_url(any_service).split("/", 1)[0]

    def repository_url(self, service: str) -> str:
        """Return the ECR repository URL for a service from Terraform output.

        Args:
            service (str): The service name (e.g., "backend", "frontend").

        Returns:
            str: The full ECR repository URL.

        Raises:
            RunnerError: If the Terraform output command fails.

        """
        self.commands.require("terraform")
        live_dir = self.root_dir / LIVE_DIR
        result = self.commands.run(
            "terraform",
            f"-chdir={live_dir}",
            "output",
            "-raw",
            f"{service}_ecr_repository_url",
            capture_output=True,
        )
        if result.returncode != 0:
            message = f"terraform output {service}_ecr_repository_url failed: {result.stderr}"
            raise RunnerError(message)
        return result.stdout.strip()
