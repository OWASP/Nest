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
				*smoke*) ;; \
				*) filters="$$filters -filter=tests/$$filename" ;; \
			esac; \
		done; \
		[ -n "$$filters" ] || continue; \
		echo "Testing $$module_dir..."; \
		terraform -chdir="$$module_dir" init -backend=false -input=false && \
		terraform -chdir="$$module_dir" test $$filters || exit 1; \
	done

test-infrastructure-smoke: ## Run infrastructure smoke tests against LocalStack
	@bash infrastructure/scripts/run-smoke-tests.sh
