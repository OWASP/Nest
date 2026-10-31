.PHONY: test-backend test-backend-fuzz backend-test backend-test-fuzz \
	backend-test-run-fuzz backend-test-unit

include backend/make/clusterfuzz.mk

test-backend: ## Run backend tests
	@$(MAKE) backend-test

test-backend-fuzz: ## Run REST API and GraphQL fuzz tests
	@$(MAKE) backend-test-fuzz

# Implementation targets.

BACKEND_TEST_WORKERS := $(shell echo $$(( ($(shell getconf _NPROCESSORS_ONLN) + 1) / 2 )))
export BACKEND_TEST_PROJECT
FUZZ_COMPOSE = docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml

backend-test:
	@$(MAKE) backend-test-unit

backend-test-unit:
	@backend_test_project="$${BACKEND_TEST_PROJECT:-nest-backend-test-$$$$-$${RANDOM}-$${RANDOM}}"
	backend_test_image="nest-test-backend:$${backend_test_project}"
	trap 'docker image rm "$${backend_test_image}" >/dev/null 2>&1 || true' EXIT
	args=(
		'-q'
		'--cache-from=nest-test-backend'
		'-f=docker/backend/Dockerfile.unit-tests'
		backend
		'-t=nest-test-backend'
		"-t=$${backend_test_image}"
	)
	DOCKER_BUILDKIT=1 docker build "$${args[@]}" 1>/dev/null
	backend_test_compose=(
		docker compose
		'--project-name' "$${backend_test_project}"
		'-f=docker-compose/backend-test/compose.yaml'
	)
	trap '"$${backend_test_compose[@]}" down --volumes --remove-orphans; docker image rm "$${backend_test_image}" >/dev/null' EXIT
	"$${backend_test_compose[@]}" up --detach --wait db
	args=(
		'-e=DJANGO_SETTINGS_MODULE=settings.test'
		'-e=PYTEST_XDIST_AUTO_NUM_WORKERS=$(BACKEND_TEST_WORKERS)'
		'--env-file=backend/.env.unit-tests'
		'-e=DJANGO_DB_HOST=db'
		'-e=DJANGO_DB_NAME=nest_db_unit'
		'-e=DJANGO_DB_USER=nest_user_unit'
		'-e=DJANGO_DB_PORT=5432'
		"--network=$${backend_test_project}_default"
		'--rm'
		"$${backend_test_image}"
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
