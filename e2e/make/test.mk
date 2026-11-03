.PHONY: test-e2e e2e-load-data e2e-db-init e2e-test e2e-test-no-db-init \
	e2e-test-run-backend e2e-test-ui e2e-test-ui-no-db-init

test-e2e: ## Run e2e tests
	@$(MAKE) e2e-test

# Implementation targets.

E2E_COMPOSE = docker compose --project-name nest-e2e -f docker-compose/e2e/compose.yaml

e2e-db-init: fetch-nest-dump
	@docker container rm -f e2e-nest-db >/dev/null 2>&1 || true
	docker volume rm -f nest-e2e_e2e-db-data >/dev/null 2>&1 || true
	build_args=(build -q backend)
	DOCKER_BUILDKIT=1 $(E2E_COMPOSE) "$${build_args[@]}" 1>/dev/null
	up_args=(
		up
		'--abort-on-container-exit'
		'--attach=data-loader'
		'--no-build'
		'--quiet-pull'
		backend
		cache
		db
		data-loader
		'--remove-orphans'
	)
	DOCKER_BUILDKIT=1 $(E2E_COMPOSE) "$${up_args[@]}"

e2e-load-data:
	@$(MAKE) backend-data-load-e2e

e2e-test:
	@$(MAKE) e2e-db-init
	@$(MAKE) e2e-test-no-db-init

e2e-test-no-db-init:
	@build_args=(build -q backend frontend e2e-tests)
	DOCKER_BUILDKIT=1 $(E2E_COMPOSE) "$${build_args[@]}" 1>/dev/null
	up_args=(
		up
		'--abort-on-container-exit'
		'--attach=e2e-tests'
		'--no-build'
		'--quiet-pull'
		backend
		cache
		db
		frontend
		e2e-tests
		'--remove-orphans'
	)
	DOCKER_BUILDKIT=1 $(E2E_COMPOSE) "$${up_args[@]}"

e2e-test-run-backend:
	@up_args=(
		up
		'--build'
		'--remove-orphans'
		'--abort-on-container-exit'
		backend
		db
		cache
	)
	DOCKER_BUILDKIT=1 $(E2E_COMPOSE) "$${up_args[@]}"

e2e-test-ui:
	@$(MAKE) e2e-db-init
	@$(MAKE) e2e-test-ui-no-db-init

e2e-test-ui-no-db-init:
	@build_args=(build -q backend frontend e2e-tests)
	DOCKER_BUILDKIT=1 $(E2E_COMPOSE) "$${build_args[@]}" 1>/dev/null
	up_args=(
		up
		'--abort-on-container-exit'
		'--attach=e2e-tests'
		'--no-build'
		'--quiet-pull'
		backend
		cache
		db
		frontend
		e2e-tests
		'--remove-orphans'
	)
	DOCKER_BUILDKIT=1 E2E_TEST_COMMAND="pnpm run test:e2e:ui" $(E2E_COMPOSE) "$${up_args[@]}"
