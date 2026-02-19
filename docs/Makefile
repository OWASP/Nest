clean-docs-docker:
	@docker container rm -f nest-docs >/dev/null 2>&1 || true
	@docker image rm -f docker-docs >/dev/null 2>&1 || true
	@docker volume rm -f docker_docs-venv >/dev/null 2>&1 || true

update-docs-dependencies:
	cd docs && poetry update