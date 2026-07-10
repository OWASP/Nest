#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

# --- Config -------------------------------------------------------------

# Using a unique container name to avoid conflicts with unrelated localstack containers.
LOCALSTACK_CONTAINER_NAME = "nest-localstack"
LOCALSTACK_HEALTH_URL = "http://localhost:4566/_localstack/info"
HEALTH_MAX_ATTEMPTS = 30
HEALTH_POLL_INTERVAL = 2

# S3 bucket override files, used to disable prevent_destroy during tests.
# Format: (file_path, resource_name)
OVERRIDES = [
    (
        "infrastructure/modules/storage/modules/s3-bucket/test_override.tf",
        "aws_s3_bucket.this",
    ),
    (
        "infrastructure/modules/storage/modules/shared-data-bucket/test_override.tf",
        "aws_s3_bucket.nest_shared_data",
    ),
]


class TestRunnerError(Exception):
    """Custom exception for errors during test runner execution."""

    pass


# --- Helpers --------------------------------------------------------------


def require_cmd(cmd):
    if not shutil.which(cmd):
        raise TestRunnerError(f"required command '{cmd}' not found on PATH.")


def localstack_healthy(log_error=False):
    try:
        req = urllib.request.Request(LOCALSTACK_HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except Exception as e:
        if log_error:
            print(f"Health check connection error: {e}", file=sys.stderr)
        return False


def localstack_license_activated(log_error=False):
    try:
        req = urllib.request.Request(LOCALSTACK_HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("is_license_activated") is True
    except Exception as e:
        if log_error:
            print(f"License check connection error: {e}", file=sys.stderr)
    return False


def get_localstack_image_info(root_dir):
    dockerfile_path = os.path.join(root_dir, "docker/localstack/Dockerfile")
    if not os.path.exists(dockerfile_path):
        raise TestRunnerError(f"Dockerfile not found at {dockerfile_path}")

    with open(dockerfile_path, "r") as f:
        content = f.read()

    match_line = None
    # Note: This assumes a single-stage Dockerfile and returns the first matching FROM line.
    # If the Dockerfile is changed to a multi-stage build, this logic should be updated
    # to identify the correct target stage image.
    for line in content.splitlines():
        if re.match(r"^FROM\s+localstack/localstack(?:-pro)?:", line):
            match_line = line
            break

    if not match_line:
        raise TestRunnerError(
            f"could not determine LocalStack image from {dockerfile_path}."
        )

    full_image = re.sub(r"^FROM\s+", "", match_line).strip()

    match_tag = re.search(
        r"^FROM\s+localstack/localstack(?:-pro)?:\s*([^\s@]+)", match_line
    )
    if not match_tag:
        raise TestRunnerError(
            f"could not determine LocalStack image tag from {dockerfile_path}."
        )

    tag = match_tag.group(1)
    return full_image, tag


def check_existing_overrides():
    for filepath, _ in OVERRIDES:
        if os.path.exists(filepath):
            raise TestRunnerError(
                f"{filepath} already exists. Refusing to run to avoid overwriting."
            )


def write_override_files():
    print("Writing override files...")
    for filepath, resource in OVERRIDES:
        resource_type, _, resource_name = resource.partition(".")
        content = f'resource "{resource_type}" "{resource_name}" {{\n  lifecycle {{\n    prevent_destroy = false\n  }}\n}}\n'
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(content)
        except Exception as e:
            raise TestRunnerError(f"Error writing override file {filepath}: {e}")


def cleanup(localstack_started):
    print("Cleaning up override files...")
    for filepath, _ in OVERRIDES:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Warning: failed to remove {filepath}: {e}", file=sys.stderr)

    if localstack_started:
        print("Stopping and removing LocalStack container...")
        # Note: Best-effort container cleanup. We intentionally swallow any exceptions
        # during stop/rm to avoid crashing the runner or masking the original test results.
        subprocess.run(
            ["docker", "stop", LOCALSTACK_CONTAINER_NAME],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["docker", "rm", LOCALSTACK_CONTAINER_NAME],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def start_localstack(localstack_image):
    auth_token = os.environ.get("LOCALSTACK_AUTH_TOKEN")
    if not auth_token:
        raise TestRunnerError(
            "LOCALSTACK_AUTH_TOKEN environment variable is not set.\n"
            "LocalStack integration tests require a valid auth token to run."
        )

    # Clean up any lingering container with our project-specific name from a previous failed run.
    subprocess.run(
        ["docker", "rm", "-f", LOCALSTACK_CONTAINER_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("Starting LocalStack container...")
    # Passing the env variable via "-e LOCALSTACK_AUTH_TOKEN" safely forwards the token
    # from the Python process's environment without exposing it in the process argv.
    cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        LOCALSTACK_CONTAINER_NAME,
        "-p",
        "4566:4566",
        "-e",
        "LOCALSTACK_AUTH_TOKEN",
        localstack_image,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        raise TestRunnerError(f"Error starting LocalStack container: {e}")


def wait_localstack_ready():
    print("Waiting for LocalStack to become healthy...")
    for attempt in range(1, HEALTH_MAX_ATTEMPTS + 1):
        if localstack_healthy():
            break
        if attempt == HEALTH_MAX_ATTEMPTS:
            # Output the underlying connection error on the final attempt
            localstack_healthy(log_error=True)
            raise TestRunnerError(
                f"LocalStack failed to become healthy within {HEALTH_MAX_ATTEMPTS * HEALTH_POLL_INTERVAL} seconds."
            )
        print(f"Waiting... (attempt {attempt}/{HEALTH_MAX_ATTEMPTS})")
        time.sleep(HEALTH_POLL_INTERVAL)

    print("Waiting for LocalStack license activation...")
    license_max_attempts = 15
    for attempt in range(1, license_max_attempts + 1):
        if localstack_license_activated():
            break
        if attempt == license_max_attempts:
            # Output the underlying connection error on the final attempt
            localstack_license_activated(log_error=True)
            subprocess.run(
                ["docker", "logs", "--tail", "30", LOCALSTACK_CONTAINER_NAME]
            )
            raise TestRunnerError(
                f"LocalStack license failed to activate within {license_max_attempts * HEALTH_POLL_INTERVAL} seconds."
            )
        time.sleep(HEALTH_POLL_INTERVAL)

    print("LocalStack is ready!")


def _find_test_dirs(search_paths):
    test_dirs = []
    for path in search_paths:
        if os.path.exists(path):
            for root, dirs, _ in os.walk(path):
                if ".terraform" not in root and "tests" in dirs:
                    test_dirs.append(os.path.join(root, "tests"))
    return sorted(test_dirs)


def _match_test_mode(entry, mode):
    if not entry.endswith(".tftest.hcl"):
        return False
    # Integration tests are named 'integration.tftest.hcl' or end with '.integration.tftest.hcl'
    is_integration = entry == "integration.tftest.hcl" or entry.endswith(
        ".integration.tftest.hcl"
    )
    return (mode == "integration" and is_integration) or (
        mode == "unit" and not is_integration
    )


def _find_test_files(test_dir, mode):
    try:
        return [
            entry for entry in os.listdir(test_dir) if _match_test_mode(entry, mode)
        ]
    except Exception as e:
        raise TestRunnerError(f"could not read {test_dir}: {e}")


def _run_module_tests(module_dir, test_files):
    init_cmd = [
        "terraform",
        f"-chdir={module_dir}",
        "init",
        "-backend=false",
        "-input=false",
    ]
    if subprocess.run(init_cmd).returncode != 0:
        raise TestRunnerError(f"terraform init failed in {module_dir}")

    test_cmd = ["terraform", f"-chdir={module_dir}", "test"]
    for test_file in sorted(test_files):
        test_cmd.append(f"-filter=tests/{test_file}")

    if subprocess.run(test_cmd).returncode != 0:
        raise TestRunnerError(f"terraform test failed in {module_dir}")


def discover_and_run_tests(mode):
    search_paths = ["infrastructure/bootstrap", "infrastructure/modules"]
    test_dirs = _find_test_dirs(search_paths)
    test_count = 0

    for test_dir in test_dirs:
        test_files = _find_test_files(test_dir, mode)
        if not test_files:
            continue

        module_dir = os.path.dirname(test_dir)
        print(
            f"Testing {'integration' if mode == 'integration' else 'unit'} for {module_dir}..."
        )
        _run_module_tests(module_dir, test_files)
        test_count += 1

    if test_count == 0:
        raise TestRunnerError(f"No {mode} tests were found or executed.")


# --- Main -------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Infrastructure unit and integration test runner"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unit", action="store_true", help="Run unit tests (default)")
    group.add_argument(
        "--integration", action="store_true", help="Run integration tests"
    )
    group.add_argument(
        "--get-tag", action="store_true", help="Print LocalStack image tag and exit"
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "../.."))
    os.chdir(root_dir)

    # Configure Terraform plugin cache directory to save disk space and speed up tests
    cache_dir = os.path.expanduser("~/.terraform.d/plugin-cache")
    try:
        os.makedirs(cache_dir, exist_ok=True)
        os.environ["TF_PLUGIN_CACHE_DIR"] = cache_dir
    except Exception as e:
        print(f"Warning: could not configure TF_PLUGIN_CACHE_DIR: {e}", file=sys.stderr)

    try:
        if args.get_tag:
            _, tag = get_localstack_image_info(root_dir)
            print(tag)
            return

        # Check executable commands based on requirements
        require_cmd("terraform")

        if args.integration:
            require_cmd("docker")

            full_image, _ = get_localstack_image_info(root_dir)
            check_existing_overrides()

            localstack_started = False
            try:
                if localstack_healthy():
                    print("Using already running LocalStack instance.")
                else:
                    print(
                        "LocalStack is not running on port 4566. Attempting to start it..."
                    )
                    start_localstack(full_image)
                    localstack_started = True
                    wait_localstack_ready()

                write_override_files()
                discover_and_run_tests("integration")
                print("All integration tests executed successfully!")
            finally:
                cleanup(localstack_started)
        else:
            # Default mode: unit tests
            discover_and_run_tests("unit")
            print("All unit tests executed successfully!")
    except TestRunnerError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
