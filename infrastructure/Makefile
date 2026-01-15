test-infrastructure:
	@for dir in infrastructure/modules/*/; do \
		if [ -d "$$dir/tests" ]; then \
			echo "Testing $$dir..."; \
			terraform -chdir="$$dir" init -backend=false -input=false && \
			terraform -chdir="$$dir" test || exit 1; \
		fi \
	done
