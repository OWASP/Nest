"""Tests for ``scripts.deploy_services``."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.commands import CommandRunner
from scripts.deploy_services import (
    BACKEND_PORT,
    FRONTEND_PORT,
    STACK_PREFIX,
    DeployServices,
)
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
            ReplicationGroupId=f"{STACK_PREFIX}-cache"
        )

    def test_db_port(self, tmp_path: Path) -> None:
        rds = MagicMock()
        rds.describe_db_instances.return_value = {"DBInstances": [{"Endpoint": {"Port": 5432}}]}
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=rds) as mock_aws:
            assert deployer._db_port() == 5432

        mock_aws.assert_called_once_with("rds", localstack=deployer.localstack)
        rds.describe_db_instances.assert_called_once_with(
            DBInstanceIdentifier=f"{STACK_PREFIX}-db"
        )

    def test_security_group_id(self, tmp_path: Path) -> None:
        ec2 = MagicMock()
        ec2.describe_security_groups.return_value = {"SecurityGroups": [{"GroupId": "sg-123"}]}
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=ec2) as mock_aws:
            assert deployer._security_group_id("nest-local-backend-sg") == "sg-123"

        mock_aws.assert_called_once_with("ec2", localstack=deployer.localstack)
        ec2.describe_security_groups.assert_called_once_with(
            Filters=[{"Name": "group-name", "Values": ["nest-local-backend-sg"]}]
        )

    def test_run_task(self, tmp_path: Path) -> None:
        ecs = MagicMock()
        ecs.run_task.return_value = {"tasks": [{"taskArn": "arn:task"}]}
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=ecs) as mock_aws:
            arn = deployer._run_task("cluster", "sg-123", f"{STACK_PREFIX}-backend", ["subnet-1"])

        assert arn == "arn:task"
        mock_aws.assert_called_once_with("ecs", localstack=deployer.localstack)
        ecs.run_task.assert_called_once_with(
            cluster="cluster",
            launchType="FARGATE",
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": ["subnet-1"],
                    "securityGroups": ["sg-123"],
                    "assignPublicIp": "ENABLED",
                }
            },
            taskDefinition=f"{STACK_PREFIX}-backend",
        )

    def test_wait_for_task_running_success(self, tmp_path: Path) -> None:
        ecs = MagicMock()
        ecs.describe_tasks.return_value = {"tasks": [{"lastStatus": "RUNNING"}]}
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=ecs) as mock_aws:
            deployer._wait_for_task_running("cluster", "arn:task", "Backend")

        mock_aws.assert_called_once_with("ecs", localstack=deployer.localstack)
        ecs.describe_tasks.assert_called_once_with(cluster="cluster", tasks=["arn:task"])

    def test_wait_for_task_running_stopped(self, tmp_path: Path) -> None:
        ecs = MagicMock()
        ecs.describe_tasks.return_value = {
            "tasks": [{"lastStatus": "STOPPED", "stoppedReason": "boom"}]
        }
        deployer = build_deployer(tmp_path)

        with (
            patch("scripts.deploy_services.aws_client", return_value=ecs),
            pytest.raises(InfrastructureError, match="STOPPED: boom"),
        ):
            deployer._wait_for_task_running("cluster", "arn:task", "Backend")

    def test_wait_for_task_running_timeout(self, tmp_path: Path) -> None:
        ecs = MagicMock()
        ecs.describe_tasks.return_value = {"tasks": [{"lastStatus": "PENDING"}]}
        deployer = build_deployer(tmp_path)

        with (
            patch("scripts.deploy_services.aws_client", return_value=ecs),
            patch("scripts.deploy_services.time.sleep"),
            pytest.raises(InfrastructureError, match="did not become RUNNING"),
        ):
            deployer._wait_for_task_running("cluster", "arn:task", "Backend")

    def test_task_docker_ip(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout="nest-abc123\nnest-xyz\n"),
            subprocess.CompletedProcess([], 0, stdout="172.17.0.7\n"),
        ]
        deployer = build_deployer(tmp_path, commands=commands)

        arn = f"arn:aws:ecs:us-east-2:123:task/{STACK_PREFIX}/abc123"
        assert deployer._task_docker_ip(arn) == "172.17.0.7"

        commands.run.assert_any_call(
            "docker", "ps", "--format", "{{.Names}}", capture_output=True, check=True
        )
        commands.run.assert_any_call(
            "docker",
            "inspect",
            "nest-abc123",
            "--format",
            "{{.NetworkSettings.Networks.bridge.IPAddress}}",
            capture_output=True,
            check=True,
        )

    def test_task_docker_ip_not_found(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = subprocess.CompletedProcess([], 0, stdout="nest-xyz\n")
        deployer = build_deployer(tmp_path, commands=commands)

        arn = f"arn:aws:ecs:us-east-2:123:task/{STACK_PREFIX}/abc123"
        with pytest.raises(InfrastructureError, match="Could not find Docker container"):
            deployer._task_docker_ip(arn)

    def test_register_target(self, tmp_path: Path) -> None:
        elbv2 = MagicMock()
        deployer = build_deployer(tmp_path)

        with patch("scripts.deploy_services.aws_client", return_value=elbv2) as mock_aws:
            deployer._register_target("arn:tg", "172.17.0.7", BACKEND_PORT)

        mock_aws.assert_called_once_with("elbv2", localstack=deployer.localstack)
        elbv2.register_targets.assert_called_once_with(
            TargetGroupArn="arn:tg", Targets=[{"Id": "172.17.0.7", "Port": BACKEND_PORT}]
        )

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

    def test_deploy_service(self, tmp_path: Path) -> None:
        deployer = build_deployer(tmp_path)

        with (
            patch.object(DeployServices, "_security_group_id", return_value="sg-123") as mock_sg,
            patch.object(DeployServices, "_run_task", return_value="arn:task") as mock_run,
            patch.object(DeployServices, "_wait_for_task_running") as mock_wait,
            patch.object(DeployServices, "_task_docker_ip", return_value="172.17.0.7") as mock_ip,
            patch.object(DeployServices, "_register_target") as mock_register,
        ):
            arn = deployer._deploy_service(
                cluster="nest-local-backend",
                sg_name="nest-local-backend-sg",
                tg_arn="arn:tg",
                task_definition=f"{STACK_PREFIX}-backend",
                port=BACKEND_PORT,
                subnets=["subnet-1"],
                service_name="Backend",
            )

        assert arn == "arn:task"
        mock_sg.assert_called_once_with("nest-local-backend-sg")
        mock_run.assert_called_once_with(
            "nest-local-backend", "sg-123", f"{STACK_PREFIX}-backend", ["subnet-1"]
        )
        mock_wait.assert_called_once_with("nest-local-backend", "arn:task", "Backend")
        mock_ip.assert_called_once_with("arn:task")
        mock_register.assert_called_once_with("arn:tg", "172.17.0.7", BACKEND_PORT)

    def test_run_executes_workflow(self, tmp_path: Path) -> None:
        outputs = {
            "tasks_subnet_ids": ["subnet-1", "subnet-2"],
            "backend_cluster_name": "nest-local-backend",
            "backend_target_group_arn": "arn:tg:backend",
            "frontend_cluster_name": "nest-local-frontend",
            "frontend_target_group_arn": "arn:tg:frontend",
            "alb_dns_name": "nest-alb.localhost.localstack.cloud",
        }

        with (
            patch.object(DeployServices, "_terraform_outputs", return_value=outputs),
            patch.object(DeployServices, "_set_runtime_parameters") as mock_runtime,
            patch.object(
                DeployServices,
                "_deploy_service",
                side_effect=["arn:task:backend", "arn:task:frontend"],
            ) as mock_deploy,
            patch.object(DeployServices, "_check_health") as mock_health,
            patch.object(DeployServices, "_log_summary") as mock_summary,
        ):
            commands = MagicMock(spec=CommandRunner)
            deployer = DeployServices(commands, localstack=MagicMock(spec=LocalStack))
            deployer.run()

        commands.require.assert_any_call("tflocal")
        commands.require.assert_any_call("docker")
        mock_runtime.assert_called_once()
        assert mock_deploy.call_count == 2
        mock_deploy.assert_any_call(
            cluster="nest-local-backend",
            sg_name="nest-local-backend-sg",
            tg_arn="arn:tg:backend",
            task_definition=f"{STACK_PREFIX}-backend",
            port=BACKEND_PORT,
            subnets=["subnet-1", "subnet-2"],
            service_name="Backend",
        )
        mock_deploy.assert_any_call(
            cluster="nest-local-frontend",
            sg_name="nest-local-frontend-sg",
            tg_arn="arn:tg:frontend",
            task_definition=f"{STACK_PREFIX}-frontend",
            port=FRONTEND_PORT,
            subnets=["subnet-1", "subnet-2"],
            service_name="Frontend",
        )
        mock_health.assert_any_call("arn:tg:backend", "Backend")
        mock_health.assert_any_call("arn:tg:frontend", "Frontend")
        mock_summary.assert_called_once_with(
            "nest-alb.localhost.localstack.cloud", "arn:task:backend", "arn:task:frontend"
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
