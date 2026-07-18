.PHONY: cspell-dependency-audit

cspell-dependency-audit:
	@echo "Auditing cspell npm dependencies..."
	@$(MAKE) code-checks CMD='cd cspell && pnpm audit --audit-level=high'
