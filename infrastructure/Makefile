##@ Infrastructure

test-infrastructure: ## Run infrastructure tests
	@find infrastructure/modules \
		-name "tests" \
		-type d \
		-not -path "*/.terraform/*" \
		-print0 | \
	while IFS= read -r -d '' test_dir; do \
		module_dir=$$(dirname "$$test_dir"); \
		echo "Testing $$module_dir..."; \
		terraform -chdir="$$module_dir" init -backend=false -input=false && \
		terraform -chdir="$$module_dir" test || exit 1; \
	done

TERRAFORM_DOCS_VERSION := v0.22.0

docs-infrastructure: ## Generate terraform-docs
	@echo "Verifying terraform-docs version..."
	@if ! terraform-docs --version | grep -q "$(TERRAFORM_DOCS_VERSION)"; then \
		echo "Error: Required terraform-docs version is $(TERRAFORM_DOCS_VERSION)"; \
		echo "Please install it: go install github.com/terraform-docs/terraform-docs@$(TERRAFORM_DOCS_VERSION)"; \
		exit 1; \
	fi
	@cd $(dir $(abspath $(lastword $(MAKEFILE_LIST)))) && \
	find bootstrap live state modules \
		-name "main.tf" \
		-not -path "*/.terraform/*" \
		-not -path "*/tests/*" \
		-print0 | \
	while IFS= read -r -d '' tf; do \
		dir=$$(dirname "$$tf"); \
		echo "Generating docs for $$dir..."; \
		terraform-docs markdown "$$dir" \
		--config .terraform-docs.yaml \
		--output-file README.md \
		--output-mode inject || exit 1; \
	done
