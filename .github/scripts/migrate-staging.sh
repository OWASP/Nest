#!/usr/bin/env bash

set -euo pipefail

: "${BACKEND_IMAGE:?Set BACKEND_IMAGE to the published release image}"

# Use the existing staging task's roles and network before Terraform starts new services.
OUTPUTS=$(terraform -chdir=infrastructure/live output -json)
CLUSTER=$(jq -er '.tasks_cluster_name.value' <<< "$OUTPUTS")
SECURITY_GROUP=$(jq -er '.tasks_security_group_id.value' <<< "$OUTPUTS")
SUBNETS=$(jq -er '.tasks_subnet_ids.value | join(",")' <<< "$OUTPUTS")

DEFINITION=$(aws ecs describe-task-definition --task-definition "${MIGRATE_TASK_DEFINITION:?Set MIGRATE_TASK_DEFINITION}" \
  | jq --arg image "$BACKEND_IMAGE" '.taskDefinition
      | del(.taskDefinitionArn, .revision, .status, .requiresAttributes,
            .compatibilities, .registeredAt, .registeredBy, .deregisteredAt)
      | .containerDefinitions[0].image = $image')
TASK_DEFINITION=$(aws ecs register-task-definition --cli-input-json "$DEFINITION" \
  --query 'taskDefinition.taskDefinitionArn' --output text)
RESPONSE=$(aws ecs run-task --cluster "$CLUSTER" --task-definition "$TASK_DEFINITION" \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=DISABLED}")
TASK=$(jq -er 'if (.failures | length) == 0 and (.tasks | length) == 1
  then .tasks[0].taskArn else error("Migration task did not start") end' <<< "$RESPONSE")

aws ecs wait tasks-stopped --cluster "$CLUSTER" --tasks "$TASK"
EXIT_CODE=$(aws ecs describe-tasks --cluster "$CLUSTER" --tasks "$TASK" \
  --query 'tasks[0].containers[0].exitCode' --output text)
if [[ "$EXIT_CODE" != "0" ]]; then
  echo "::error::Migration task $TASK failed with exit code $EXIT_CODE"
  exit 1
fi
echo "Migrate task completed successfully"
