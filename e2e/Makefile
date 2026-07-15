##@ End-to-end tests

# Repository root (this file lives in e2e/). Use the repository root Makefile so
# `make -C e2e <target>` works the same as `make <target>` from the repo root.
REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

.PHONY: audit-e2e-dependencies \
	init-e2e-db \
	test-e2e \
	test-e2e-no-db-init \
	test-e2e-ui \
	test-e2e-ui-no-db-init

audit-e2e-dependencies: ## Audit e2e npm dependencies
	@echo "Auditing e2e npm dependencies..."
	@cd $(REPO_ROOT)/e2e && pnpm audit --audit-level=$(AUDIT_LEVEL)

init-e2e-db:
	@$(MAKE) -C $(REPO_ROOT) fetch-nest-dump
	@docker container rm -f e2e-nest-db >/dev/null 2>&1 || true
	@docker volume rm -f nest-e2e_e2e-db-data >/dev/null 2>&1 || true
	@cd $(REPO_ROOT) && DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml build -q backend \
		1>/dev/null
	@cd $(REPO_ROOT) && DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml up \
		--abort-on-container-exit \
		--attach data-loader \
		--no-build \
		--quiet-pull \
		backend cache db data-loader \
		--remove-orphans

test-e2e: ## Run e2e tests (DB init, then full stack + Playwright)
	@$(MAKE) init-e2e-db
	@$(MAKE) test-e2e-no-db-init

test-e2e-no-db-init:
	@cd $(REPO_ROOT) && DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml build -q backend frontend e2e-tests \
		1>/dev/null
	@cd $(REPO_ROOT) && DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml up \
		--abort-on-container-exit \
		--attach e2e-tests \
		--no-build \
		--quiet-pull \
		backend cache db frontend e2e-tests \
		--remove-orphans

test-e2e-ui: ## Run e2e tests in Playwright UI mode
	@$(MAKE) init-e2e-db
	@$(MAKE) test-e2e-ui-no-db-init

test-e2e-ui-no-db-init:
	@cd $(REPO_ROOT) && DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml build -q backend frontend e2e-tests \
		1>/dev/null
	@cd $(REPO_ROOT) && DOCKER_BUILDKIT=1 E2E_TEST_COMMAND="pnpm run test:e2e:ui" docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml up \
		--abort-on-container-exit \
		--attach e2e-tests \
		--no-build \
		--quiet-pull \
		backend cache db frontend e2e-tests \
		--remove-orphans
