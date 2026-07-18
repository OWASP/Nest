.PHONY: test-e2e e2e-db-init e2e-test e2e-test-no-db-init e2e-test-ui e2e-test-ui-no-db-init

test-e2e: ## Run e2e tests
	@$(MAKE) e2e-test

# Implementation targets.

e2e-db-init:
	@$(MAKE) fetch-nest-dump
	@docker container rm -f e2e-nest-db >/dev/null 2>&1 || true
	@docker volume rm -f nest-e2e_e2e-db-data >/dev/null 2>&1 || true
	@DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml build -q backend \
		1>/dev/null
	@DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml up \
		--abort-on-container-exit \
		--attach data-loader \
		--no-build \
		--quiet-pull \
		backend cache db data-loader \
		--remove-orphans

e2e-test:
	@$(MAKE) e2e-db-init
	@$(MAKE) e2e-test-no-db-init

e2e-test-no-db-init:
	@DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml build -q backend frontend e2e-tests \
		1>/dev/null
	@DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml up \
		--abort-on-container-exit \
		--attach e2e-tests \
		--no-build \
		--quiet-pull \
		backend cache db frontend e2e-tests \
		--remove-orphans

e2e-test-ui:
	@$(MAKE) e2e-db-init
	@$(MAKE) e2e-test-ui-no-db-init

e2e-test-ui-no-db-init:
	@DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml build -q backend frontend e2e-tests \
		1>/dev/null
	@DOCKER_BUILDKIT=1 E2E_TEST_COMMAND="pnpm run test:e2e:ui" docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml up \
		--abort-on-container-exit \
		--attach e2e-tests \
		--no-build \
		--quiet-pull \
		backend cache db frontend e2e-tests \
		--remove-orphans
