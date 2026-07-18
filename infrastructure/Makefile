.PHONY: test-infrastructure

test-infrastructure: ## Run infrastructure tests
	@if [ -n "$$CI" ]; then \
		sh infrastructure/scripts/run-tests.sh; \
	else \
		docker run \
		--rm \
		--entrypoint /bin/sh \
		-e HOME=/tmp \
		-e TF_PLUGIN_CACHE_DIR=/tmp/terraform-plugin-cache \
		-v "$(CURDIR):/work" \
		--mount type=volume,src=nest-infrastructure-terraform-plugin-cache,dst=/tmp/terraform-plugin-cache \
		-w /work \
		$$(grep -E '^FROM hashicorp/terraform:' docker/code-checks/Dockerfile | sed 's/^FROM //; s/ AS .*//') \
		infrastructure/scripts/run-tests.sh; \
	fi
