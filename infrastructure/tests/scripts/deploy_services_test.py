"""Tests for ``scripts.deploy_services``."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.commands import CommandRunner
from scripts.deploy_services import DeployServices
from scripts.errors import CommandNotFoundError, InfrastructureError
from scripts.localstack import LocalStack


def build_deployer(
    tmp_path: Path,
    commands: MagicMock | None = None,
    localstack: MagicMock | None = None,
) -> DeployServices:
    deployer = DeployServices(
        commands or MagicMock(spec=CommandRunner),
        localstack=localstack or MagicMock(spec=LocalStack),
    )
    deployer.root_dir = tmp_path
    deployer.infra_dir = tmp_path / "infrastructure"
    deployer.live_dir = deployer.infra_dir / "live"
    return deployer


class TestDeployServices:
    """Tests for ``DeployServices``."""

    @patch.dict(os.environ, {}, clear=True)
    def test_prefix_defaults_to_local(self, tmp_path: Path) -> None:
        deployer = build_deployer(tmp_path)
        assert deployer.prefix == "/nest/local"

    @patch.dict(os.environ, {"ENVIRONMENT": "dev"}, clear=True)
    def test_prefix_uses_environment(self, tmp_path: Path) -> None:
        deployer = build_deployer(tmp_path)
        assert deployer.prefix == "/nest/dev"

    @patch.dict(os.environ, {}, clear=True)
    def test_stack_prefix_defaults_to_local(self, tmp_path: Path) -> None:
        deployer = build_deployer(tmp_path)
        assert deployer.stack_prefix == "nest-local"

    @patch.dict(os.environ, {"ENVIRONMENT": "dev"}, clear=True)
    def test_stack_prefix_uses_environment(self, tmp_path: Path) -> None:
        deployer = build_deployer(tmp_path)
        assert deployer.stack_prefix == "nest-dev"

    @patch.dict(os.environ, {"ENVIRONMENT": "staging", "PROJECT_NAME": "owasp-nest"}, clear=True)
    def test_stack_prefix_uses_project_name(self, tmp_path: Path) -> None:
        deployer = build_deployer(tmp_path)
        assert deployer.stack_prefix == "owasp-nest-staging"

    def test_terraform_outputs(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        raw_output = (
            '{"alb_dns_name": {"value": "dns"}, "tasks_subnet_ids": {"value": ["subnet-1"]}}'
        )
        commands.run.return_value = subprocess.CompletedProcess([], 0, stdout=raw_output)
        deployer = build_deployer(tmp_path, commands=commands)

        assert deployer._terraform_outputs() == {
            "alb_dns_name": "dns",
            "tasks_subnet_ids": ["subnet-1"],
        }
        commands.run.assert_called_once_with(
            "tflocal",
            "output",
            "-json",
            cwd=deployer.live_dir,
            capture_output=True,
            check=False,
        )

    def test_terraform_outputs_failure(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = subprocess.CompletedProcess([], 1, stdout="")
        deployer = build_deployer(tmp_path, commands=commands)

        with pytest.raises(InfrastructureError, match="provision-infra"):
            deployer._terraform_outputs()

    def test_terraform_outputs_invalid_json(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = subprocess.CompletedProcess([], 0, stdout="not json")
        deployer = build_deployer(tmp_path, commands=commands)

        with pytest.raises(InfrastructureError, match="tflocal output"):
            deployer._terraform_outputs()

    def test_container_ip(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = subprocess.CompletedProcess([], 0, stdout="172.17.0.2\n")
        localstack = MagicMock(spec=LocalStack)
        localstack.container_name = "nest-localstack"
        deployer = build_deployer(tmp_path, commands=commands, localstack=localstack)

        assert deployer._container_ip() == "172.17.0.2"
        commands.run.assert_called_once_with(
            "docker",
            "inspect",
            "nest-localstack",
            "--format",
            "{{.NetworkSettings.Networks.bridge.IPAddress}}",
            capture_output=True,
            check=True,
        )

    def test_set_runtime_parameters(self, tmp_path: Path) -> None:
        deployer = build_deployer(tmp_path)

        with (
            patch.object(DeployServices, "_container_ip", return_value="172.17.0.2"),
            patch.object(DeployServices, "_redis_port", return_value=6379),
            patch.object(DeployServices, "_db_port", return_value=5432),
            patch.object(DeployServices, "_put_ssm") as mock_put,
        ):
            deployer._set_runtime_parameters()

        mock_put.assert_any_call("/nest/local/DJANGO_REDIS_HOST", "172.17.0.2")
        mock_put.assert_any_call("/nest/local/DJANGO_REDIS_PORT", "6379")
        mock_put.assert_any_call("/nest/local/DJANGO_DB_HOST", "172.17.0.2")
        mock_put.assert_any_call("/nest/local/DJANGO_DB_PORT", "5432")

    def test_put_ssm(self, tmp_path: Path) -> None:
        ssm = MagicMock()
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=ssm) as mock_aws:
            deployer._put_ssm("/nest/local/DJANGO_REDIS_HOST", "172.17.0.2")

        mock_aws.assert_called_once_with("ssm", localstack=deployer.localstack)
        ssm.put_parameter.assert_called_once_with(
            Name="/nest/local/DJANGO_REDIS_HOST",
            Value="172.17.0.2",
            Type="String",
            Overwrite=True,
        )

    def test_redis_port(self, tmp_path: Path) -> None:
        elasticache = MagicMock()
        elasticache.describe_replication_groups.return_value = {
            "ReplicationGroups": [{"NodeGroups": [{"PrimaryEndpoint": {"Port": 6379}}]}]
        }
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=elasticache) as mock_aws:
            assert deployer._redis_port() == 6379

        mock_aws.assert_called_once_with("elasticache", localstack=deployer.localstack)
        elasticache.describe_replication_groups.assert_called_once_with(
            ReplicationGroupId=f"{deployer.stack_prefix}-cache"
        )

    def test_db_port(self, tmp_path: Path) -> None:
        rds = MagicMock()
        rds.describe_db_instances.return_value = {"DBInstances": [{"Endpoint": {"Port": 5432}}]}
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=rds) as mock_aws:
            assert deployer._db_port() == 5432

        mock_aws.assert_called_once_with("rds", localstack=deployer.localstack)
        rds.describe_db_instances.assert_called_once_with(
            DBInstanceIdentifier=f"{deployer.stack_prefix}-db"
        )

    def test_start_service(self, tmp_path: Path) -> None:
        ecs = MagicMock()
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=ecs) as mock_aws:
            deployer._start_service("nest-local-backend", "nest-local-backend-service", "Backend")

        mock_aws.assert_called_once_with("ecs", localstack=deployer.localstack)
        ecs.update_service.assert_any_call(
            cluster="nest-local-backend", service="nest-local-backend-service", desiredCount=0
        )
        ecs.update_service.assert_any_call(
            cluster="nest-local-backend", service="nest-local-backend-service", desiredCount=1
        )

    def test_wait_for_service_running(self, tmp_path: Path) -> None:
        ecs = MagicMock()
        ecs.describe_services.return_value = {"services": [{"runningCount": 1, "desiredCount": 1}]}
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=ecs) as mock_aws:
            deployer._wait_for_service("cluster", "svc", "Backend")

        mock_aws.assert_called_once_with("ecs", localstack=deployer.localstack)
        ecs.describe_services.assert_called_once_with(cluster="cluster", services=["svc"])

    def test_wait_for_service_timeout(self, tmp_path: Path) -> None:
        ecs = MagicMock()
        ecs.describe_services.return_value = {"services": [{"runningCount": 0, "desiredCount": 1}]}
        deployer = build_deployer(tmp_path)

        with (
            patch("scripts.deploy_services.aws_client", return_value=ecs),
            patch("scripts.deploy_services.time.sleep"),
            pytest.raises(InfrastructureError, match="did not reach desired count"),
        ):
            deployer._wait_for_service("cluster", "svc", "Backend")

    def test_wait_for_service_missing(self, tmp_path: Path) -> None:
        ecs = MagicMock()
        ecs.describe_services.return_value = {"services": []}
        deployer = build_deployer(tmp_path)

        with (
            patch("scripts.deploy_services.aws_client", return_value=ecs),
            patch("scripts.deploy_services.time.sleep"),
            pytest.raises(InfrastructureError, match="did not reach desired count"),
        ):
            deployer._wait_for_service("cluster", "svc", "Backend")

    def test_check_health_healthy(self, tmp_path: Path) -> None:
        elbv2 = MagicMock()
        elbv2.describe_target_health.return_value = {
            "TargetHealthDescriptions": [{"TargetHealth": {"State": "healthy"}}]
        }
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=elbv2):
            deployer._check_health("arn:tg", "Backend")

    def test_check_health_timeout(self, tmp_path: Path) -> None:
        elbv2 = MagicMock()
        elbv2.describe_target_health.return_value = {
            "TargetHealthDescriptions": [{"TargetHealth": {"State": "unhealthy"}}]
        }
        deployer = build_deployer(tmp_path)

        with (
            patch("scripts.deploy_services.aws_client", return_value=elbv2),
            patch("scripts.deploy_services.time.sleep"),
            pytest.raises(InfrastructureError, match="did not become healthy"),
        ):
            deployer._check_health("arn:tg", "Backend")

    def test_run_executes_workflow(self, tmp_path: Path) -> None:
        outputs = {
            "backend_cluster_name": "nest-local-backend",
            "backend_service_name": "nest-local-backend-service",
            "backend_target_group_arn": "arn:tg:backend",
            "frontend_cluster_name": "nest-local-frontend",
            "frontend_service_name": "nest-local-frontend-service",
            "frontend_target_group_arn": "arn:tg:frontend",
            "alb_dns_name": "nest-alb.localhost.localstack.cloud",
        }

        with (
            patch.object(DeployServices, "_terraform_outputs", return_value=outputs),
            patch.object(DeployServices, "_set_runtime_parameters") as mock_runtime,
            patch.object(DeployServices, "_start_service") as mock_start,
            patch.object(DeployServices, "_wait_for_service") as mock_wait,
            patch.object(DeployServices, "_check_health") as mock_health,
            patch.object(DeployServices, "_log_summary") as mock_summary,
        ):
            commands = MagicMock(spec=CommandRunner)
            deployer = DeployServices(commands, localstack=MagicMock(spec=LocalStack))
            deployer.run()

        commands.require.assert_any_call("tflocal")
        commands.require.assert_any_call("docker")
        mock_runtime.assert_called_once()
        assert mock_start.call_count == 2
        mock_start.assert_any_call("nest-local-backend", "nest-local-backend-service", "Backend")
        mock_start.assert_any_call(
            "nest-local-frontend", "nest-local-frontend-service", "Frontend"
        )
        assert mock_wait.call_count == 2
        mock_wait.assert_any_call("nest-local-backend", "nest-local-backend-service", "Backend")
        mock_wait.assert_any_call("nest-local-frontend", "nest-local-frontend-service", "Frontend")
        mock_health.assert_any_call("arn:tg:backend", "Backend")
        mock_health.assert_any_call("arn:tg:frontend", "Frontend")
        mock_summary.assert_called_once_with(
            "nest-alb.localhost.localstack.cloud",
            "nest-local-backend-service",
            "nest-local-frontend-service",
        )

    @pytest.mark.parametrize("missing", ["tflocal", "docker"])
    def test_run_requires_prerequisites(self, tmp_path: Path, missing: str) -> None:
        commands = MagicMock(spec=CommandRunner)

        def missing_command(command: str) -> None:
            if command == missing:
                raise CommandNotFoundError(missing)

        commands.require.side_effect = missing_command
        deployer = DeployServices(commands, localstack=MagicMock(spec=LocalStack))

        with pytest.raises(CommandNotFoundError, match=missing):
            deployer.run()

        commands.run.assert_not_called()
