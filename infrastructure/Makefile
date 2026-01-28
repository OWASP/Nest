test-infrastructure:
	@find infrastructure/modules \
		-name "tests" \
		-not -path "*/.terraform/*" \
		-print0 \
		-type d | \
	while IFS= read -r -d '' test_dir; do \
		module_dir=$$(dirname "$$test_dir"); \
		echo "Testing $$module_dir..."; \
		terraform -chdir="$$module_dir" init -backend=false -input=false && \
		terraform -chdir="$$module_dir" test || exit 1; \
	done
