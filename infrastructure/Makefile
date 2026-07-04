##@ Infrastructure

MAKEFILE_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

start-localstack: ## Start LocalStack (requires .env with LOCALSTACK_AUTH_TOKEN)
	@$(MAKEFILE_DIR)scripts/start-localstack.sh

provision-infra: ## Create resource on localstack and push images
	@$(MAKEFILE_DIR)scripts/provision-infra.sh

load-env-params: ## Upload local .env variables to LocalStack SSM Parameter Store
	@$(MAKEFILE_DIR)scripts/load-env-params.sh $(ARGS)

test-infrastructure: ## Run infrastructure tests
	@find $(MAKEFILE_DIR)bootstrap $(MAKEFILE_DIR)modules \
		-name "tests" \
		-type d \
		-not -path "*/.terraform/*" | \
	while IFS= read -r test_dir; do \
		module_dir=$$(dirname "$$test_dir"); \
		echo "Testing $$module_dir..."; \
		terraform -chdir="$$module_dir" init -backend=false -input=false && \
		terraform -chdir="$$module_dir" test || exit 1; \
	done
