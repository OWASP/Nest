#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_LIVE_DIR="$(cd "$SCRIPT_DIR/../live" && pwd)"

ENV_FILE="$SCRIPT_DIR/../.env"

source "$SCRIPT_DIR/check-prerequisites.sh"

if [[ -f "$ENV_FILE" ]]; then
    set -a && source "$ENV_FILE" && set +a
fi

AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-2}"

check_prerequisites awslocal tflocal jq docker

cd "$INFRA_LIVE_DIR"

TF_OUTPUTS=$(tflocal output -json 2>/dev/null) || {
    echo "ERROR: Failed to get Terraform outputs. Run 'make provision-infra' first." >&2
    exit 1
}

echo "Deploying ECS services..."

# Fix DJANGO_REDIS_HOST to use the LocalStack container IP instead of
# localhost.localstack.cloud (which resolves to loopback inside ECS tasks).
LOCALSTACK_CONTAINER_IP=$(docker inspect localstack-main --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')
SSM_PREFIX="/nest/local"
echo "  Setting DJANGO_REDIS_HOST to LocalStack container IP: $LOCALSTACK_CONTAINER_IP"
AWS_PAGER="" awslocal ssm put-parameter \
    --region "$AWS_DEFAULT_REGION" \
    --name "$SSM_PREFIX/DJANGO_REDIS_HOST" \
    --value "$LOCALSTACK_CONTAINER_IP" \
    --type "String" \
    --overwrite \
    --output text >/dev/null

# Discover the actual Redis port from Elasticache (LocalStack ignores the
# configured port and assigns one from its port range).
ACTUAL_REDIS_PORT=$(awslocal elasticache describe-replication-groups \
    --region "$AWS_DEFAULT_REGION" \
    --replication-group-id "nest-local-cache" \
    --query "ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Port" \
    --output text)
echo "  Setting DJANGO_REDIS_PORT to actual Elasticache port: $ACTUAL_REDIS_PORT"
AWS_PAGER="" awslocal ssm put-parameter \
    --region "$AWS_DEFAULT_REGION" \
    --name "$SSM_PREFIX/DJANGO_REDIS_PORT" \
    --value "$ACTUAL_REDIS_PORT" \
    --type "String" \
    --overwrite \
    --output text >/dev/null

ACTUAL_DB_PORT=$(AWS_PAGER="" awslocal rds describe-db-instances \
    --region "$AWS_DEFAULT_REGION" \
    --db-instance-identifier "nest-local-db" \
    --query "DBInstances[0].Endpoint.Port" \
    --output text)

echo "  Setting DJANGO_DB_HOST to LocalStack container IP: $LOCALSTACK_CONTAINER_IP"
AWS_PAGER="" awslocal ssm put-parameter \
    --region "$AWS_DEFAULT_REGION" \
    --name "$SSM_PREFIX/DJANGO_DB_HOST" \
    --value "$LOCALSTACK_CONTAINER_IP" \
    --type "String" \
    --overwrite \
    --output text >/dev/null

echo "  Setting DJANGO_DB_PORT to actual RDS port: $ACTUAL_DB_PORT"
AWS_PAGER="" awslocal ssm put-parameter \
    --region "$AWS_DEFAULT_REGION" \
    --name "$SSM_PREFIX/DJANGO_DB_PORT" \
    --value "$ACTUAL_DB_PORT" \
    --type "String" \
    --overwrite \
    --output text >/dev/null

get_tf_output() {
    local key="$1"
    echo "$TF_OUTPUTS" | jq -r ".[\"$key\"].value"
}

get_sg_id() {
    local name="$1"
    awslocal ec2 describe-security-groups \
        --filters "Name=group-name,Values=$name" \
        --region "$AWS_DEFAULT_REGION" \
        --query "SecurityGroups[0].GroupId" \
        --output text
}

wait_for_task_running() {
    local cluster="$1"
    local task_arn="$2"
    local service_name="$3"
    local max_attempts=30
    local attempt=0

    echo "  Waiting for $service_name task to be RUNNING..."
    while [[ $attempt -lt $max_attempts ]]; do
        status=$(awslocal ecs describe-tasks \
            --cluster "$cluster" \
            --tasks "$task_arn" \
            --region "$AWS_DEFAULT_REGION" \
            --query "tasks[0].lastStatus" \
            --output text)

        if [[ "$status" == "RUNNING" ]]; then
            echo "  $service_name task is RUNNING."
            return 0
        fi

        if [[ "$status" == "STOPPED" ]]; then
            stop_code=$(awslocal ecs describe-tasks \
                --cluster "$cluster" \
                --tasks "$task_arn" \
                --region "$AWS_DEFAULT_REGION" \
                --query "tasks[0].stoppedReason" \
                --output text)
            echo "  ERROR: $service_name task STOPPED: $stop_code" >&2
            return 1
        fi

        sleep 5
        ((attempt++)) || true
    done

    echo "  ERROR: $service_name task did not become RUNNING after $((max_attempts * 5)) seconds." >&2
    return 1
}

get_task_docker_ip() {
    local task_arn="$1"
    local task_id="${task_arn##*/}"
    local container
    container=$(docker ps --format '{{.Names}}' | grep "$task_id" | head -1) || true

    if [[ -z "$container" ]]; then
        echo "  ERROR: Could not find Docker container for task $task_id" >&2
        return 1
    fi

    docker inspect "$container" --format '{{.NetworkSettings.Networks.bridge.IPAddress}}'
}

STACK_PREFIX="nest-local"
PUBLIC_SUBNETS=$(get_tf_output "tasks_subnet_ids" | jq -r 'join(",")')

echo ""
echo "--- Backend ---"

BACKEND_CLUSTER=$(get_tf_output "backend_cluster_name")
BACKEND_SG=$(get_sg_id "${STACK_PREFIX}-backend-sg")
BACKEND_TG_ARN=$(get_tf_output "backend_target_group_arn")

echo "  Cluster: $BACKEND_CLUSTER"
echo "  Security Group: $BACKEND_SG"
echo "  Target Group ARN: $BACKEND_TG_ARN"

BACKEND_TASK=$(awslocal ecs run-task \
    --cluster "$BACKEND_CLUSTER" \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$PUBLIC_SUBNETS],securityGroups=[$BACKEND_SG],assignPublicIp=ENABLED}" \
    --task-definition "${STACK_PREFIX}-backend" \
    --region "$AWS_DEFAULT_REGION" \
    --query "tasks[0].taskArn" \
    --output text)

echo "  Task ARN: $BACKEND_TASK"

wait_for_task_running "$BACKEND_CLUSTER" "$BACKEND_TASK" "Backend"

BACKEND_IP=$(get_task_docker_ip "$BACKEND_TASK")
echo "  Backend Docker bridge IP: $BACKEND_IP"

echo "  Registering backend target with ALB..."
awslocal elbv2 register-targets \
    --target-group-arn "$BACKEND_TG_ARN" \
    --targets "Id=$BACKEND_IP,Port=8000" \
    --region "$AWS_DEFAULT_REGION"

echo ""
echo "--- Frontend ---"

FRONTEND_CLUSTER=$(get_tf_output "frontend_cluster_name")
FRONTEND_SG=$(get_sg_id "${STACK_PREFIX}-frontend-sg")
FRONTEND_TG_ARN=$(get_tf_output "frontend_target_group_arn")

echo "  Cluster: $FRONTEND_CLUSTER"
echo "  Security Group: $FRONTEND_SG"
echo "  Target Group ARN: $FRONTEND_TG_ARN"

FRONTEND_TASK=$(awslocal ecs run-task \
    --cluster "$FRONTEND_CLUSTER" \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$PUBLIC_SUBNETS],securityGroups=[$FRONTEND_SG],assignPublicIp=ENABLED}" \
    --task-definition "${STACK_PREFIX}-frontend" \
    --region "$AWS_DEFAULT_REGION" \
    --query "tasks[0].taskArn" \
    --output text)

echo "  Task ARN: $FRONTEND_TASK"

wait_for_task_running "$FRONTEND_CLUSTER" "$FRONTEND_TASK" "Frontend"

FRONTEND_IP=$(get_task_docker_ip "$FRONTEND_TASK")
echo "  Frontend Docker bridge IP: $FRONTEND_IP"

echo "  Registering frontend target with ALB..."
awslocal elbv2 register-targets \
    --target-group-arn "$FRONTEND_TG_ARN" \
    --targets "Id=$FRONTEND_IP,Port=3000" \
    --region "$AWS_DEFAULT_REGION"

echo ""
echo "--- Health Checks ---"

ALB_DNS=$(get_tf_output "alb_dns_name")
echo "  ALB DNS: $ALB_DNS"

sleep 5

check_health() {
    local tg_arn="$1"
    local service="$2"
    local max_attempts=36

    for ((i = 1; i <= max_attempts; i++)); do
        local health
        health=$(awslocal elbv2 describe-target-health \
            --target-group-arn "$tg_arn" \
            --region "$AWS_DEFAULT_REGION" \
            --query "TargetHealthDescriptions[0].TargetHealth.State" \
            --output text 2>/dev/null)

        if [[ "$health" == "healthy" ]]; then
            echo "  $service target group health: healthy"
            return 0
        fi

        echo "  $service target group: $health (attempt $i/$max_attempts)"
        sleep 10
    done

    echo "  ERROR: $service target did not become healthy." >&2
    return 1
}

check_health "$BACKEND_TG_ARN" "Backend"
check_health "$FRONTEND_TG_ARN" "Frontend"

echo ""
echo "--- Deployment Complete ---"
echo "  ALB DNS: $ALB_DNS"
echo "  Backend: https://$ALB_DNS/status/"
echo "  Frontend: https://$ALB_DNS/"
echo ""
echo "  Backend task: $BACKEND_TASK"
echo "  Frontend task: $FRONTEND_TASK"
