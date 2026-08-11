.PHONY: test-docs docs-test docs-test-image-build

test-docs: ## Run docs tests
	@$(MAKE) docs-test

# Implementation targets.

DOCS_TEST_IMAGE = nest-test-docs

docs-test:
	@$(MAKE) docs-test-image-build
	@docker run --rm $(DOCS_TEST_IMAGE)

docs-test-image-build:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from $(DOCS_TEST_IMAGE) \
		-f docker/docs/Dockerfile.tests . \
		-t $(DOCS_TEST_IMAGE) 1>/dev/null
