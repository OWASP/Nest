.PHONY: infrastructure-dependency-audit

infrastructure-dependency-audit:
	@echo "Auditing infrastructure Python dependencies..."
	@$(MAKE) code-checks CMD='cd infrastructure && \
		poetry export -f requirements.txt --without-hashes --with test -o /tmp/requirements.txt && \
		pip-audit -r /tmp/requirements.txt'
