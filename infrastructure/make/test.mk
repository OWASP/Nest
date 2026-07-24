.PHONY: test-infrastructure test-infrastructure-integration test-infrastructure-unit \
	infrastructure-test infrastructure-test-image-build \
	infrastructure-test-integration infrastructure-test-unit \
	test-infrastructure-smoke

test-infrastructure: ## Run infrastructure tests
	@$(MAKE) infrastructure-test

test-infrastructure-integration:
	@$(MAKE) infrastructure-test-integration

test-infrastructure-unit:
	@$(MAKE) infrastructure-test-unit \
	test-infrastructure-smoke

# Implementation targets.

INFRASTRUCTURE_COMPOSE = docker compose \
	--project-name nest-infrastructure \
	-f docker-compose/infrastructure/compose.yaml

INFRASTRUCTURE_TEST_IMAGE = nest-test-infrastructure

# Integration tests write these override files; clean them up before and after a run.
INFRASTRUCTURE_TEST_OVERRIDES = \
	infrastructure/modules/storage/modules/s3-bucket/test_override.tf \
	infrastructure/modules/storage/modules/shared-data-bucket/test_override.tf

infrastructure-test:
	@$(MAKE) infrastructure-test-unit \
	test-infrastructure-smoke
	@$(MAKE) infrastructure-test-integration

infrastructure-test-image-build:
	@DOCKER_BUILDKIT=1 docker build -q \
		--build-context terraform=docker-image://$(TERRAFORM_IMAGE) \
		--cache-from $(INFRASTRUCTURE_TEST_IMAGE) \
		-f docker/infrastructure/Dockerfile.tests . \
		-t $(INFRASTRUCTURE_TEST_IMAGE) 1>/dev/null

infrastructure-test-unit:
	@$(MAKE) infrastructure-test-image-build
	@docker run --rm \
		-v "$(CURDIR)/infrastructure/bootstrap:/home/owasp/infrastructure/bootstrap" \
		-v "$(CURDIR)/infrastructure/modules:/home/owasp/infrastructure/modules" \
		-v "$(CURDIR)/infrastructure/scripts:/home/owasp/infrastructure/scripts:ro" \
		-v "$(CURDIR)/infrastructure/tests:/home/owasp/infrastructure/tests:ro" \
		$(INFRASTRUCTURE_TEST_IMAGE)

infrastructure-test-integration:
	@if [ -z "$$LOCALSTACK_AUTH_TOKEN" ]; then \
		if [ -t 2 ]; then \
			printf '\033[1;33mWarning:\033[0m Skipping infrastructure integration tests: LOCALSTACK_AUTH_TOKEN is not set.\n' >&2; \
		else \
			echo "Warning: Skipping infrastructure integration tests: LOCALSTACK_AUTH_TOKEN is not set." >&2; \
		fi; \
		exit 0; \
	fi; \
	$(MAKE) infrastructure-test-image-build || exit $$?; \
	status=0; \
	trap '$(INFRASTRUCTURE_COMPOSE) down --volumes --remove-orphans >/dev/null 2>&1 || true; rm -f $(INFRASTRUCTURE_TEST_OVERRIDES)' EXIT; \
	rm -f $(INFRASTRUCTURE_TEST_OVERRIDES); \
	COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
		$(INFRASTRUCTURE_COMPOSE) up \
			--abort-on-container-exit \
			--build \
			--exit-code-from tests \
		|| status=$$?; \
	exit $$status

test-infrastructure-smoke: ## Run infrastructure smoke tests against LocalStack
	@bash infrastructure/scripts/run-smoke-tests.sh
