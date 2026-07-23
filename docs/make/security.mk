.PHONY: docs-dependency-audit

docs-dependency-audit:
	@echo "Auditing docs Python dependencies..."
	@$(MAKE) run-cmd CMD='cd docs && \
		poetry export -f requirements.txt --without-hashes --only main -o /tmp/requirements.txt && \
		pip-audit -r /tmp/requirements.txt'
