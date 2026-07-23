.PHONY: infrastructure-dependency-audit

infrastructure-dependency-audit:
	@echo "Auditing infrastructure Python dependencies..."
	@$(MAKE) run-cmd CMD='cd infrastructure && \
		poetry export -f requirements.txt --with test -o /tmp/infrastructure-requirements.txt && \
		pip-audit --disable-pip -r /tmp/infrastructure-requirements.txt'
