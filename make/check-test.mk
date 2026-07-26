##@ Checks and tests

.PHONY: check-test check-test-backend check-test-frontend check-test-e2e check-test-infrastructure

check-test: ## Run code quality checks and tests
	@$(MAKE) check
	@$(MAKE) test

check-test-backend: ## Run code quality checks and backend tests
	@$(MAKE) check
	@$(MAKE) test-backend

check-test-frontend: ## Run code quality checks and frontend tests
	@$(MAKE) check
	@$(MAKE) test-frontend

check-test-e2e: ## Run code quality checks and e2e tests
	@$(MAKE) check
	@$(MAKE) test-e2e

check-test-infrastructure: ## Run code quality checks and infrastructure tests
	@$(MAKE) check
	@$(MAKE) test-infrastructure
