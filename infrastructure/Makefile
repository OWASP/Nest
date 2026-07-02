##@ Infrastructure

test-infrastructure: ## Run infrastructure tests
	@find infrastructure/bootstrap infrastructure/modules \
		-name "tests" \
		-type d \
		-not -path "*/.terraform/*" | \
	while IFS= read -r test_dir; do \
		module_dir=$$(dirname "$$test_dir"); \
	filters=""; \
		for test_file in "$$test_dir"/*.tftest.hcl; do \
			[ -e "$$test_file" ] || continue; \
		filename=$$(basename "$$test_file"); \
			case "$$filename" in \
				*integration*) ;; \
				*) filters="$$filters -filter=tests/$$filename" ;; \
			esac; \
		done; \
		if [ -n "$$filters" ]; then \
			echo "Testing $$module_dir..."; \
			terraform -chdir="$$module_dir" init -backend=false -input=false && \
			terraform -chdir="$$module_dir" test $$filters || exit 1; \
		fi; \
	done

test-infrastructure-integration: ## Run infrastructure integration tests
	@./infrastructure/scripts/run-integration-tests.sh
