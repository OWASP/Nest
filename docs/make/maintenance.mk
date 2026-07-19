.PHONY: docs-clean-docker

docs-clean-docker:
	@docker container rm -f nest-docs >/dev/null 2>&1 || true
	@docker image rm -f nest-local-docs >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_docs-venv >/dev/null 2>&1 || true
