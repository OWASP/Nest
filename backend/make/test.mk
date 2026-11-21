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
	@$(MAKE) backend-test-contributions

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
		tests/unit
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

.PHONY: backend-test-contributions
backend-test-contributions: ## Run contribution regression tests against isolated PostgreSQL
	@docker build -q -f docker/backend/Dockerfile.unit-tests -t nest-test-backend backend
	@set -eu; \
	name="nest-contribution-tests-$$$$"; \
	trap 'docker rm -fv "$$name" >/dev/null 2>&1 || true' EXIT; \
	docker run -d --name "$$name" -e POSTGRES_USER=nest_test -e POSTGRES_PASSWORD=integration-test -e POSTGRES_DB=nest_test pgvector/pgvector:pg16@sha256:ccc6e83d6e35e931dc7c5def2022729d5a6c370318d099181995567ff1fb4d6b >/dev/null; \
	ready=false; attempt=0; \
	while [ "$$attempt" -lt 30 ]; do \
		if docker exec "$$name" pg_isready -U nest_test >/dev/null 2>&1; then ready=true; break; fi; \
			attempt=$$((attempt + 1)); sleep 1; \
		done; \
	if [ "$$ready" != true ]; then echo "PostgreSQL did not become ready" >&2; exit 1; fi; \
		docker run --rm --network "container:$$name" --env-file backend/.env.unit-tests \
		-e DJANGO_SETTINGS_MODULE=settings.test -e DJANGO_DB_HOST=localhost \
		-e DJANGO_DB_PORT=5432 -e DJANGO_DB_NAME=nest_test -e DJANGO_DB_USER=nest_test \
		-e DJANGO_DB_PASSWORD=integration-test nest-test-backend \
		pytest -o addopts='' tests/integration/github -q
