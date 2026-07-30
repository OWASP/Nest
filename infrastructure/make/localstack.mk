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
	@infrastructure/scripts/start-localstack.sh

provision-infra: ## Create resource on localstack and push images
	@infrastructure/scripts/provision-infra.sh

load-env-params: ## Upload local .env variables to LocalStack SSM Parameter Store
	@infrastructure/scripts/load-env-params.sh $(ARGS)

deploy-services: ## Run backend/frontend ECS tasks on Fargate and register ALB targets
	@infrastructure/scripts/deploy-services.sh

ecs-migrate: ## Run database migrations on LocalStack
	$(call RUN_ECS_TASK,migrate)

ecs-load-data: ## Load initial data on LocalStack
	$(call RUN_ECS_TASK,load-data)

ecs-index-data: ## Index data for search on LocalStack
	$(call RUN_ECS_TASK,index-data)

ecs-task: ## Run an ECS task (set TASK=name, e.g. make ecs-task TASK=migrate)
	$(call RUN_ECS_TASK,$(TASK))

deploy-on-localstack: ## Full LocalStack provision: infra + images + SSM params + deploy services
	@infrastructure/scripts/provision-infra.sh && \
	$infrastructure/scripts/load-env-params.sh --overwrite && \
	$infrastructure/scripts/deploy-services.sh
