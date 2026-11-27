.PHONY: docs-dependency-audit

docs-dependency-audit:
	@echo "Auditing docs Python dependencies..."
	@$(MAKE) code-checks CMD='cd docs && \
		req=$$(mktemp) && trap "rm -f \"$$req\"" EXIT && \
		poetry export -f requirements.txt --only main -o "$$req" && \
		pip-audit --disable-pip -r "$$req"'
