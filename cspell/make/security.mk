.PHONY: cspell-dependency-audit

cspell-dependency-audit:
	@echo "Auditing cspell npm dependencies..."
	@$(MAKE) run-cmd CMD='cd cspell && pnpm audit --audit-level=moderate'
