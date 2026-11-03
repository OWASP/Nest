.PHONY: test-backend test-backend-fuzz backend-test backend-test-fuzz \
	backend-test-run-fuzz backend-test-unit

include backend/make/clusterfuzz.mk

test-backend: ## Run backend tests
	@$(MAKE) backend-test

test-backend-fuzz: ## Run REST API and GraphQL fuzz tests
	@$(MAKE) backend-test-fuzz

# Implementation targets.

BACKEND_TEST_WORKERS := $(shell echo $$(( ($(shell getconf _NPROCESSORS_ONLN) + 1) / 2 )))
FUZZ_COMPOSE = docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml

backend-test:
	@$(MAKE) backend-test-unit

backend-test-unit:
	@args=(
		'-q'
		'--cache-from=nest-test-backend'
		'-f=docker/backend/Dockerfile.unit-tests'
		backend
		'-t=nest-test-backend'
	)
	DOCKER_BUILDKIT=1 docker build "$${args[@]}" 1>/dev/null
	args=(
		'-e=DJANGO_SETTINGS_MODULE=settings.test'
		'-e=PYTEST_XDIST_AUTO_NUM_WORKERS=$(BACKEND_TEST_WORKERS)'
		'--env-file=backend/.env.unit-tests'
		'--rm'
		nest-test-backend
		pytest
	)
	docker run "$${args[@]}"

backend-test-fuzz:
	@docker container rm -f fuzz-nest-db >/dev/null 2>&1 || true
	docker volume rm -f nest-fuzz_fuzz-db-data >/dev/null 2>&1 || true
	up_args=(
		up
		'--build'
		'--remove-orphans'
		'--abort-on-container-exit'
		backend
		cache
		data-loader
		db
	)
	COMPOSE_BAKE=true DOCKER_BUILDKIT=1 $(FUZZ_COMPOSE) "$${up_args[@]}"
	echo "Running REST API fuzz tests..."
	up_args=(
		up
		'--build'
		'--remove-orphans'
		'--abort-on-container-exit'
		backend
		db
		rest
	)
	COMPOSE_BAKE=true DOCKER_BUILDKIT=1 $(FUZZ_COMPOSE) "$${up_args[@]}"
	echo "Running GraphQL fuzz tests..."
	up_args=(
		up
		'--build'
		'--remove-orphans'
		'--abort-on-container-exit'
		backend
		cache
		db
		graphql
	)
	COMPOSE_BAKE=true DOCKER_BUILDKIT=1 $(FUZZ_COMPOSE) "$${up_args[@]}"

backend-test-run-fuzz:
	@up_args=(
		up
		'--build'
		'--remove-orphans'
		'--abort-on-container-exit'
		backend
		cache
		db
	)
	COMPOSE_BAKE=true DOCKER_BUILDKIT=1 $(FUZZ_COMPOSE) "$${up_args[@]}"
