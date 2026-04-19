##@ Infrastructure

TERRAFORM_DOCS_VERSION := v0.22.0

docs-infrastructure: ## Generate Terraform documentation for all modules and projects
	@command -v terraform-docs >/dev/null 2>&1 || { \
		echo "terraform-docs is not installed. Install it with:"; \
		echo "  brew install terraform-docs"; \
		exit 1; \
		}
	@current=$$(terraform-docs --version 2>&1 | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1); \
	if [ "$$current" != "$(TERRAFORM_DOCS_VERSION)" ]; then \
		echo "terraform-docs version mismatch: expected $(TERRAFORM_DOCS_VERSION), got $$current"; \
		echo "  brew upgrade terraform-docs"; \
		exit 1; \
	fi
	@find infrastructure/modules infrastructure/bootstrap infrastructure/live infrastructure/state \
		-name "*.tf" \
		-not -path "*/.terraform/*" \
		-exec dirname {} \; | \
	sort -u | \
	while read -r dir; do \
		echo "Generating docs for $$dir..."; \
		terraform-docs --config infrastructure/.terraform-docs.yml "$$dir" || exit 1; \
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
