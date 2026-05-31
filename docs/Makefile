.PHONY: audit-docs-dependencies

audit-docs-dependencies: ## Audit docs Python dependencies
	@echo "Auditing docs Python dependencies..."
	@command -v pip-audit >/dev/null 2>&1 || python -m pip install -q pip-audit
	@cd docs && poetry export -f requirements.txt --without-hashes --only main | \
		pip-audit -r /dev/stdin

clean-docs-docker:
	@docker container rm -f nest-docs >/dev/null 2>&1 || true
	@docker image rm -f docker-docs >/dev/null 2>&1 || true
	@docker volume rm -f docker_docs-venv >/dev/null 2>&1 || true

update-docs-dependencies:
	cd docs && poetry update
