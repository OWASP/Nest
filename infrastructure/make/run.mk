.PHONY: infrastructure-check-auth-token infrastructure-refresh infrastructure-up

INFRASTRUCTURE_COMPOSE = docker compose \
	--project-name nest-infrastructure \
	-f docker-compose/infrastructure/compose.yaml

infrastructure-check-auth-token:
	@if [ -z "$$LOCALSTACK_AUTH_TOKEN" ]; then \
		if [ -t 2 ]; then \
			printf '\033[1;31mError:\033[0m LOCALSTACK_AUTH_TOKEN is not set.\n' >&2; \
		else \
			echo "Error: LOCALSTACK_AUTH_TOKEN is not set." >&2; \
		fi; \
		exit 1; \
	fi

infrastructure-refresh: infrastructure-check-auth-token ## Refresh an existing deployment on LocalStack
	@$(MAKE) infrastructure-image-build || exit $$?; \
	$(INFRASTRUCTURE_COMPOSE) up --wait localstack || exit $$?; \
	$(INFRASTRUCTURE_COMPOSE) run --rm runner python -m scripts.run_deploy --refresh

infrastructure-up: infrastructure-check-auth-token ## Start LocalStack and deploy infrastructure
	@$(MAKE) infrastructure-image-build || exit $$?; \
	$(INFRASTRUCTURE_COMPOSE) up --wait localstack || exit $$?; \
	$(INFRASTRUCTURE_COMPOSE) run --rm runner python -m scripts.run_deploy
