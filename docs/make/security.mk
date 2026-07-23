.PHONY: docs-dependency-audit

docs-dependency-audit:
	@echo "Auditing docs Python dependencies..."
	@$(MAKE) run-cmd CMD='cd docs && \
		poetry export -f requirements.txt --only main -o /tmp/docs-requirements.txt && \
		pip-audit --disable-pip -r /tmp/docs-requirements.txt'
