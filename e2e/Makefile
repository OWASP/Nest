##@ End-to-end tests

# Repository root (this file lives in e2e/). Use the repository root Makefile so
# `make -C e2e <target>` works the same as `make <target>` from the repo root.
REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

.PHONY: audit-e2e-dependencies \
	init-e2e-db \
	test-e2e-no-db-init \
	test-e2e \
	test-e2e-ui-no-db-init \
	test-e2e-ui \
	check-e2e \
	lint-e2e-code

check-e2e: ## Run e2e code quality checks
check-e2e: \
	lint-e2e-code 

audit-e2e-dependencies: ## Audit e2e npm dependencies
	@echo "Auditing e2e npm dependencies..."
	@cd $(REPO_ROOT)/e2e && pnpm audit --audit-level=$(AUDIT_LEVEL)

init-e2e-db:
	@$(MAKE) -C $(REPO_ROOT) fetch-nest-dump
	@docker container rm -f e2e-nest-db >/dev/null 2>&1 || true
	@docker volume rm -f nest-e2e_e2e-db-data >/dev/null 2>&1 || true
	@cd $(REPO_ROOT) && DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml up \
		--abort-on-container-exit backend cache db data-loader \
		--build \
		--remove-orphans

lint-e2e-code:
	@(cd $(REPO_ROOT)/e2e && pnpm run lint:check >/dev/null 2>&1 \
	  && (printf "pnpm run lint"; for i in $$(seq 1 60); do printf "."; done; printf "\033[30;42mPassed\033[0m\n") \
	  || (printf "pnpm run lint"; for i in $$(seq 1 60); do printf "."; done; printf "\033[37;41mFailed\033[0m\n" && pnpm run lint))

test-e2e-no-db-init:
	@cd $(REPO_ROOT) && DOCKER_BUILDKIT=1 docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml up \
		--abort-on-container-exit backend cache db frontend e2e-tests \
		--build \
		--remove-orphans

test-e2e: ## Run e2e tests (DB init, then full stack + Playwright)
	@$(MAKE) init-e2e-db
	@$(MAKE) test-e2e-no-db-init

test-e2e-ui-no-db-init:
	@cd $(REPO_ROOT) && DOCKER_BUILDKIT=1 E2E_TEST_COMMAND="pnpm run test:e2e:ui" docker compose \
		--project-name nest-e2e \
		-f docker-compose/e2e/compose.yaml up \
		--abort-on-container-exit backend cache db frontend e2e-tests \
		--build \
		--remove-orphans

test-e2e-ui: ## Run e2e tests in Playwright UI mode
	@$(MAKE) init-e2e-db
	@$(MAKE) test-e2e-ui-no-db-init
