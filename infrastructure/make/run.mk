.PHONY: infrastructure-localstack-up

INFRASTRUCTURE_COMPOSE = docker compose \
	--project-name nest-infrastructure \
	-f docker-compose/infrastructure/compose.yaml

INFRASTRUCTURE_LOCAL_IMAGE = nest-local-infrastructure

infrastructure-localstack-up: ## Start LocalStack in the foreground
	@if [ -z "$$LOCALSTACK_AUTH_TOKEN" ]; then \
		if [ -t 2 ]; then \
			printf '\033[1;31mError:\033[0m LOCALSTACK_AUTH_TOKEN is not set.\n' >&2; \
		else \
			echo "Error: LOCALSTACK_AUTH_TOKEN is not set." >&2; \
		fi; \
		exit 1; \
	fi; \
	DOCKER_BUILDKIT=1 $(INFRASTRUCTURE_COMPOSE) up --build localstack
