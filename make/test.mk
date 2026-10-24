##@ Tests

.PHONY: test

test: ## Run tests
	@$(MAKE) test-docs
	@$(MAKE) test-backend
	@$(MAKE) test-frontend
	@$(MAKE) test-e2e
