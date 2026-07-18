##@ Tests

.PHONY: test

test: ## Run tests
	@$(MAKE) test-backend
	@$(MAKE) test-frontend
	@$(MAKE) test-e2e
	@$(MAKE) test-infrastructure
