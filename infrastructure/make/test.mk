.PHONY: test-infrastructure test-infrastructure-integration test-infrastructure-unit \
	infrastructure-test infrastructure-image-build \
	infrastructure-test-integration infrastructure-test-unit

test-infrastructure: ## Run infrastructure tests
	@$(MAKE) infrastructure-test

test-infrastructure-integration:
	@$(MAKE) infrastructure-test-integration

test-infrastructure-unit:
	@$(MAKE) infrastructure-test-unit

# Implementation targets.

INFRASTRUCTURE_IMAGE = nest-infrastructure

infrastructure-test:
	@$(MAKE) infrastructure-test-unit
	@$(MAKE) infrastructure-test-integration

infrastructure-image-build:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from $(INFRASTRUCTURE_IMAGE) \
		-f docker/infrastructure/Dockerfile . \
		-t $(INFRASTRUCTURE_IMAGE) 1>/dev/null

infrastructure-test-unit:
	@$(MAKE) infrastructure-image-build
	@docker run --rm \
		-v nest-terraform-plugin-cache:/home/owasp/.terraform.d/plugin-cache \
		$(INFRASTRUCTURE_IMAGE) \
		sh -c "pytest && python -m scripts.run_tests --unit"

infrastructure-test-integration:
	@if [ -z "$$LOCALSTACK_AUTH_TOKEN" ]; then \
		if [ -t 2 ]; then \
			printf '\033[1;33mWarning:\033[0m Skipping infrastructure integration tests: LOCALSTACK_AUTH_TOKEN is not set.\n' >&2; \
		else \
			echo "Warning: Skipping infrastructure integration tests: LOCALSTACK_AUTH_TOKEN is not set." >&2; \
		fi; \
		exit 0; \
	fi; \
	$(MAKE) infrastructure-image-build || exit $$?; \
	status=0; \
	trap '$(INFRASTRUCTURE_COMPOSE) down --remove-orphans >/dev/null 2>&1 || true' EXIT; \
	COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
		$(INFRASTRUCTURE_COMPOSE) \
			-f docker-compose/infrastructure/compose.integration.yaml \
			up \
			--abort-on-container-exit \
			--build \
			--exit-code-from runner \
		|| status=$$?; \
	exit $$status
