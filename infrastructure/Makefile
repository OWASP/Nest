##@ Infrastructure

.PHONY: audit-infrastructure-dependencies build-infrastructure-test-image \
	install-infrastructure-dependencies test-infrastructure \
	test-infrastructure-integration test-infrastructure-unit \
	update-infrastructure-dependencies

INFRASTRUCTURE_COMPOSE = docker compose \
	--project-name nest-infrastructure \
	-f docker-compose/infrastructure/compose.yaml

INFRASTRUCTURE_TEST_IMAGE = nest-test-infrastructure

INFRASTRUCTURE_TEST_OVERRIDES = \
	infrastructure/modules/storage/modules/s3-bucket/test_override.tf \
	infrastructure/modules/storage/modules/shared-data-bucket/test_override.tf

install-infrastructure-dependencies:
	@cd infrastructure && poetry install --no-interaction --with test

test-infrastructure: ## Run infrastructure unit and integration tests
test-infrastructure: \
	test-infrastructure-unit \
	test-infrastructure-integration

build-infrastructure-test-image:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from $(INFRASTRUCTURE_TEST_IMAGE) \
		-f docker/infrastructure/Dockerfile.tests . \
		-t $(INFRASTRUCTURE_TEST_IMAGE) 1>/dev/null

test-infrastructure-unit: ## Run infrastructure unit tests
test-infrastructure-unit: build-infrastructure-test-image
	@docker run --rm \
		-v "$(CURDIR)/infrastructure/bootstrap:/home/owasp/infrastructure/bootstrap" \
		-v "$(CURDIR)/infrastructure/modules:/home/owasp/infrastructure/modules" \
		-v "$(CURDIR)/infrastructure/scripts:/home/owasp/infrastructure/scripts:ro" \
		-v "$(CURDIR)/infrastructure/tests:/home/owasp/infrastructure/tests:ro" \
		$(INFRASTRUCTURE_TEST_IMAGE)

test-infrastructure-integration: ## Run infrastructure integration tests
	@if [ -z "$$LOCALSTACK_AUTH_TOKEN" ]; then \
		if [ -t 2 ]; then \
			printf '\033[1;33mWarning:\033[0m Skipping infrastructure integration tests: LOCALSTACK_AUTH_TOKEN is not set.\n' >&2; \
		else \
			echo "Warning: Skipping infrastructure integration tests: LOCALSTACK_AUTH_TOKEN is not set." >&2; \
		fi; \
		exit 0; \
	fi; \
	$(MAKE) build-infrastructure-test-image; \
	status=0; \
	rm -f $(INFRASTRUCTURE_TEST_OVERRIDES); \
	COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
		$(INFRASTRUCTURE_COMPOSE) up \
			--abort-on-container-exit \
			--build \
			--exit-code-from tests \
		|| status=$$?; \
	$(INFRASTRUCTURE_COMPOSE) down --volumes --remove-orphans >/dev/null 2>&1 || true; \
	rm -f $(INFRASTRUCTURE_TEST_OVERRIDES); \
	exit $$status

audit-infrastructure-dependencies: ## Audit infrastructure Python dependencies
	@echo "Auditing infrastructure Python dependencies..."
	@command -v pip-audit >/dev/null 2>&1 || python -m pip install -q pip-audit
	@cd infrastructure && poetry export -f requirements.txt --without-hashes --with test | \
		pip-audit -r /dev/stdin

update-infrastructure-dependencies:
	cd infrastructure && poetry update
