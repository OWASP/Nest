##@ Tools

.PHONY: test-tools tools-test tools-test-image-build

test-tools: ## Run tools tests
	@$(MAKE) tools-test

# Implementation targets.

TOOLS_TEST_IMAGE = nest-test-tools

tools-test:
	@$(MAKE) tools-test-image-build
	@docker run --rm $(TOOLS_TEST_IMAGE)

tools-test-image-build:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from $(TOOLS_TEST_IMAGE) \
		-f docker/tools/Dockerfile.tests . \
		-t $(TOOLS_TEST_IMAGE) 1>/dev/null
