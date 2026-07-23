.PHONY: infrastructure-dependency-audit

infrastructure-dependency-audit:
	@echo "Auditing infrastructure Python dependencies..."
	@$(MAKE) code-checks CMD='cd infrastructure && \
		req=$$(mktemp) && trap "rm -f \"$$req\"" EXIT && \
		poetry export -f requirements.txt --with test -o "$$req" && \
		pip-audit --disable-pip -r "$$req"'
