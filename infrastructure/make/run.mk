.PHONY: infrastructure-deploy-local

INFRASTRUCTURE_COMPOSE = docker compose \
	--project-name nest-infrastructure \
	-f docker-compose/infrastructure/compose.yaml

INFRASTRUCTURE_LOCAL_IMAGE = nest-local-infrastructure

infrastructure-deploy-local: ## Deploy infrastructure to LocalStack
	@if [ -z "$$LOCALSTACK_AUTH_TOKEN" ]; then \
		if [ -t 2 ]; then \
			printf '\033[1;31mError:\033[0m LOCALSTACK_AUTH_TOKEN is not set.\n' >&2; \
		else \
			echo "Error: LOCALSTACK_AUTH_TOKEN is not set." >&2; \
		fi; \
		exit 1; \
	fi; \
	$(MAKE) infrastructure-image-build || exit $$?; \
	COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
		$(INFRASTRUCTURE_COMPOSE) \
			-f docker-compose/infrastructure/compose.deploy.yaml \
			up
