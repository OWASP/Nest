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

LOCALSTACK_CONTAINER_NAME = "localstack"
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

# --- Helpers --------------------------------------------------------------


def require_cmd(cmd):
    if not shutil.which(cmd):
        print(f"Error: required command '{cmd}' not found on PATH.", file=sys.stderr)
        sys.exit(1)


def localstack_healthy():
    try:
        req = urllib.request.Request(LOCALSTACK_HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def localstack_license_activated():
    try:
        req = urllib.request.Request(LOCALSTACK_HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("is_license_activated") is True
    except Exception:
        pass
    return False


def get_localstack_image_info(root_dir):
    dockerfile_path = os.path.join(root_dir, "docker/localstack/Dockerfile")
    if not os.path.exists(dockerfile_path):
        print(f"Error: Dockerfile not found at {dockerfile_path}", file=sys.stderr)
        sys.exit(1)

    with open(dockerfile_path, "r") as f:
        content = f.read()

    match_line = None
    for line in content.splitlines():
        if re.match(r"^FROM\s+localstack/localstack(?:-pro)?:", line):
            match_line = line
            break

    if not match_line:
        print(
            f"Error: could not determine LocalStack image from {dockerfile_path}.",
            file=sys.stderr,
        )
        sys.exit(1)

    full_image = re.sub(r"^FROM\s+", "", match_line).strip()

    match_tag = re.search(
        r"^FROM\s+localstack/localstack(?:-pro)?:\s*([^\s@]+)", match_line
    )
    if not match_tag:
        print(
            f"Error: could not determine LocalStack image tag from {dockerfile_path}.",
            file=sys.stderr,
        )
        sys.exit(1)

    tag = match_tag.group(1)
    return full_image, tag


def check_existing_overrides():
    for filepath, _ in OVERRIDES:
        if os.path.exists(filepath):
            print(
                f"Error: {filepath} already exists. Refusing to run to avoid overwriting.",
                file=sys.stderr,
            )
            sys.exit(1)


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
            print(f"Error writing override file {filepath}: {e}", file=sys.stderr)
            sys.exit(1)


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
        print(
            "Error: LOCALSTACK_AUTH_TOKEN environment variable is not set.",
            file=sys.stderr,
        )
        print(
            "LocalStack integration tests require a valid auth token to run.",
            file=sys.stderr,
        )
        sys.exit(1)

    subprocess.run(
        ["docker", "rm", "-f", LOCALSTACK_CONTAINER_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("Starting LocalStack container...")
    cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        LOCALSTACK_CONTAINER_NAME,
        "-p",
        "4566:4566",
        "-e",
        f"LOCALSTACK_AUTH_TOKEN={auth_token}",
        localstack_image,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error starting LocalStack container: {e}", file=sys.stderr)
        sys.exit(1)


def wait_localstack_ready():
    print("Waiting for LocalStack to become healthy...")
    for attempt in range(1, HEALTH_MAX_ATTEMPTS + 1):
        if localstack_healthy():
            break
        if attempt == HEALTH_MAX_ATTEMPTS:
            print(
                f"Error: LocalStack failed to become healthy within {HEALTH_MAX_ATTEMPTS * HEALTH_POLL_INTERVAL} seconds.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Waiting... (attempt {attempt}/{HEALTH_MAX_ATTEMPTS})")
        time.sleep(HEALTH_POLL_INTERVAL)

    print("Waiting for LocalStack license activation...")
    license_max_attempts = 15
    for attempt in range(1, license_max_attempts + 1):
        if localstack_license_activated():
            break
        if attempt == license_max_attempts:
            print(
                f"Error: LocalStack license failed to activate within {license_max_attempts * HEALTH_POLL_INTERVAL} seconds.",
                file=sys.stderr,
            )
            subprocess.run(
                f"docker logs {LOCALSTACK_CONTAINER_NAME} 2>&1 | tail -30", shell=True
            )
            sys.exit(1)
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
    is_integration = "integration" in entry
    return (mode == "integration" and is_integration) or (
        mode == "unit" and not is_integration
    )


def _find_test_files(test_dir, mode):
    try:
        return [
            entry
            for entry in os.listdir(test_dir)
            if _match_test_mode(entry, mode)
        ]
    except Exception as e:
        print(f"Warning: could not read {test_dir}: {e}", file=sys.stderr)
        return []


def _run_module_tests(module_dir, test_files):
    init_cmd = [
        "terraform",
        f"-chdir={module_dir}",
        "init",
        "-backend=false",
        "-input=false",
    ]
    if subprocess.run(init_cmd).returncode != 0:
        print(f"Error: terraform init failed in {module_dir}", file=sys.stderr)
        sys.exit(1)

    test_cmd = ["terraform", f"-chdir={module_dir}", "test"]
    for test_file in sorted(test_files):
        test_cmd.append(f"-filter=tests/{test_file}")

    if subprocess.run(test_cmd).returncode != 0:
        print(f"Error: terraform test failed in {module_dir}", file=sys.stderr)
        sys.exit(1)


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
        print(f"Error: No {mode} tests were found or executed.", file=sys.stderr)
        sys.exit(1)



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


if __name__ == "__main__":
    main()
