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

docs-infrastructure: ## Generate terraform-docs
	@find . \
		-name "main.tf" \
		-not -path "*/.terraform/*" \
		-not -path "*/tests/*" \
		-exec dirname {} \; | sort -u | \
	while read -r dir; do \
		echo "Generating docs for $$dir..."; \
		terraform-docs markdown "$$dir" \
		--config $(CURDIR)/.terraform-docs.yml \
		--output-file README.md \
		--output-mode inject; \
	done
