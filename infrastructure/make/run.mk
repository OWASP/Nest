.PHONY: infrastructure-check-auth-token infrastructure-ensure-local-config infrastructure-refresh infrastructure-up

DOCKER_GID := $(shell stat -c '%g' /var/run/docker.sock 2>/dev/null || stat -f '%g' /var/run/docker.sock 2>/dev/null)
export DOCKER_GID

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

infrastructure-ensure-local-config:
	@[ -f infrastructure/state/terraform.localstack.tfvars ] || \
		cp infrastructure/state/terraform.localstack.tfvars.example \
		infrastructure/state/terraform.localstack.tfvars
	@[ -f infrastructure/live/terraform.localstack.tfvars ] || \
		cp infrastructure/live/terraform.localstack.tfvars.example \
		infrastructure/live/terraform.localstack.tfvars
	@[ -f infrastructure/live/terraform.localstack.tfbackend ] || \
		cp infrastructure/live/terraform.localstack.tfbackend.example \
		infrastructure/live/terraform.localstack.tfbackend

infrastructure-refresh: infrastructure-check-auth-token infrastructure-ensure-local-config ## Refresh an existing deployment on LocalStack
	@$(MAKE) infrastructure-image-build || exit $$?; \
	$(INFRASTRUCTURE_COMPOSE) up --build --wait localstack || exit $$?; \
	$(INFRASTRUCTURE_COMPOSE) run --rm runner python -m scripts.run_deploy --refresh

infrastructure-up: infrastructure-check-auth-token infrastructure-ensure-local-config ## Start LocalStack and deploy infrastructure
	@$(MAKE) infrastructure-image-build || exit $$?; \
	$(INFRASTRUCTURE_COMPOSE) up --build --wait localstack || exit $$?; \
	$(INFRASTRUCTURE_COMPOSE) run --rm runner python -m scripts.run_deploy
