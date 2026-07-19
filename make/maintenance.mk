##@ Maintenance

.PHONY: clean graphql-codegen prune clean-dependencies clean-docker clean-trivy-cache \
	tooling-clean-dependencies

clean: ## Remove all generated files and containers
	@$(MAKE) clean-dependencies
	@$(MAKE) clean-docker
	@$(MAKE) clean-trivy-cache

graphql-codegen: ## Regenerate GraphQL types
	@CMD="pnpm run graphql-codegen" $(MAKE) frontend-exec-command

prune: ## Prune Docker resources
	@docker builder prune --filter 'until=72h' -a -f
	@docker image prune --filter 'until=72h' -a -f
	@docker volume prune -f

# Implementation targets.

clean-dependencies:
	@$(MAKE) backend-clean-dependencies
	@$(MAKE) frontend-clean-dependencies
	@$(MAKE) tooling-clean-dependencies

clean-docker:
	@$(MAKE) backend-clean-docker
	@$(MAKE) docs-clean-docker
	@$(MAKE) frontend-clean-docker

clean-trivy-cache:
	@rm -rf $(CURDIR)/.trivy-cache

tooling-clean-dependencies:
	@rm -rf node_modules
