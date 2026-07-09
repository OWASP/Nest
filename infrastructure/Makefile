##@ Infrastructure

MAKEFILE_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
AWS_REGION := us-east-2
LIVE_DIR := $(MAKEFILE_DIR)live

define RUN_ECS_TASK
	@cd $(LIVE_DIR) && \
		CLUSTER=$$(tflocal output -raw tasks_cluster_name) && \
		SUBNETS=$$(tflocal output -json tasks_subnet_ids | jq -r 'join(",")') && \
		SG=$$(tflocal output -raw tasks_security_group_id) && \
		AWS_DEFAULT_REGION=$(AWS_REGION) awslocal ecs run-task \
			--cluster $$CLUSTER \
			--launch-type FARGATE \
			--network-configuration "awsvpcConfiguration={subnets=[$$SUBNETS],securityGroups=[$$SG],assignPublicIp=ENABLED}" \
			--task-definition nest-local-$(1) \
			--region $(AWS_REGION)
endef

start-localstack: ## Start LocalStack (requires .env with LOCALSTACK_AUTH_TOKEN)
	@$(MAKEFILE_DIR)scripts/start-localstack.sh

provision-infra: ## Create resource on localstack and push images
	@$(MAKEFILE_DIR)scripts/provision-infra.sh

load-env-params: ## Upload local .env variables to LocalStack SSM Parameter Store
	@$(MAKEFILE_DIR)scripts/load-env-params.sh $(ARGS)

deploy-services: ## Run backend/frontend ECS tasks on Fargate and register ALB targets
	@$(MAKEFILE_DIR)scripts/deploy-services.sh

ecs-migrate: ## Run database migrations on LocalStack
	$(call RUN_ECS_TASK,migrate)

ecs-load-data: ## Load initial data on LocalStack
	$(call RUN_ECS_TASK,load-data)

ecs-index-data: ## Index data for search on LocalStack
	$(call RUN_ECS_TASK,index-data)

ecs-task: ## Run an ECS task (set TASK=name, e.g. make ecs-task TASK=migrate)
	$(call RUN_ECS_TASK,$(TASK))

provision: ## Full LocalStack provision: infra + images + SSM params + deploy services
	@$(MAKEFILE_DIR)scripts/provision-infra.sh --overwrite
	@$(MAKEFILE_DIR)scripts/load-env-params.sh
	@$(MAKEFILE_DIR)scripts/deploy-services.sh

test-infrastructure: ## Run infrastructure tests
	@find $(MAKEFILE_DIR)bootstrap $(MAKEFILE_DIR)modules \
		-name "tests" \
		-type d \
		-not -path "*/.terraform/*" | \
	while IFS= read -r test_dir; do \
		module_dir=$$(dirname "$$test_dir"); \
		echo "Testing $$module_dir..."; \
		terraform -chdir="$$module_dir" init -backend=false -input=false && \
		terraform -chdir="$$module_dir" test || exit 1; \
	done
