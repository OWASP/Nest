##@ Infrastructure

terraform-docs-infrastructure: ## Generate terraform-docs for infrastructure projects and modules
	@for dir in infrastructure/bootstrap infrastructure/live infrastructure/state $$(find infrastructure/modules -type f -name "*.tf" -not -path "*/.terraform/*" -exec dirname {} \; | sort -u); do \
		echo "Generating terraform-docs for $$dir..."; \
		terraform-docs --config "$(CURDIR)/infrastructure/.terraform-docs.yml" "$$dir" || exit 1; \
	done

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
