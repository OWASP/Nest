.PHONY: test-backend test-backend-fuzz backend-test backend-test-fuzz backend-test-run-e2e \
	backend-test-run-fuzz

include backend/make/clusterfuzz.mk

test-backend: ## Run backend tests
	@$(MAKE) backend-test

test-backend-fuzz: ## Run REST API and GraphQL fuzz tests
	@$(MAKE) backend-test-fuzz

# Implementation targets.

BACKEND_TEST_WORKERS := $(shell echo $$(( ($(shell getconf _NPROCESSORS_ONLN) + 1) / 2 )))

backend-test:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from nest-test-backend \
		-f docker/backend/Dockerfile.unit-tests backend \
		-t nest-test-backend 1>/dev/null
	@docker run \
		-e DJANGO_SETTINGS_MODULE=settings.test \
		-e PYTEST_XDIST_AUTO_NUM_WORKERS=$(BACKEND_TEST_WORKERS) \
		--env-file backend/.env.unit-tests \
		--rm nest-test-backend pytest

backend-test-fuzz:
	@docker container rm -f fuzz-nest-db >/dev/null 2>&1 || true
	@docker volume rm -f nest-fuzz_fuzz-db-data >/dev/null 2>&1 || true
	@COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml up --build --remove-orphans --abort-on-container-exit db cache backend data-loader
	@echo "Running REST API fuzz tests..."
	@COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml up --build --remove-orphans --abort-on-container-exit db backend rest
	@echo "Running GraphQL fuzz tests..."
	@COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml up --build --remove-orphans --abort-on-container-exit db cache backend graphql

backend-test-run-e2e:
	@DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-e2e -f docker-compose/e2e/compose.yaml up --build --remove-orphans --abort-on-container-exit backend db cache

backend-test-run-fuzz:
	@COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml up --build --remove-orphans --abort-on-container-exit backend db cache
