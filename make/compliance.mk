##@ Compliance

.PHONY: compliance-check compliance-license-check

compliance-check: ## Run compliance checks
	@$(MAKE) compliance-license-check

compliance-license-check: ## Check repository files for licenses outside the allowlist
	@echo "Running FOSSology license check..."
	python tools/compliance/fossology_license_check.py
