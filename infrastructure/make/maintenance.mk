.PHONY: infrastructure-clean-docker

infrastructure-clean-docker:
	@docker image rm -f $(INFRASTRUCTURE_TEST_IMAGE) >/dev/null 2>&1 || true
	@$(INFRASTRUCTURE_COMPOSE) down --volumes --remove-orphans >/dev/null 2>&1 || true
