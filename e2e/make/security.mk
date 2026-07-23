.PHONY: e2e-dependency-audit

e2e-dependency-audit:
	@echo "Auditing e2e npm dependencies..."
	@$(MAKE) run-cmd CMD='cd e2e && pnpm audit --audit-level=moderate'
