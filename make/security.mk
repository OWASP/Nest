##@ Security

.PHONY: security-dependency-audit security-scan security-code-scan security-image-scan \
	security-code-scan-semgrep security-code-scan-trivy security-scan-zap tooling-dependency-audit

security-dependency-audit: ## Audit all project dependencies for known vulnerabilities
	@$(MAKE) backend-dependency-audit
	@$(MAKE) cspell-dependency-audit
	@$(MAKE) docs-dependency-audit
	@$(MAKE) e2e-dependency-audit
	@$(MAKE) frontend-dependency-audit
	@$(MAKE) tooling-dependency-audit

security-scan: ## Run code and image security scans
	@$(MAKE) security-code-scan
	@$(MAKE) security-image-scan

security-code-scan: ## Run code security scans only
	@$(MAKE) security-code-scan-semgrep
	@$(MAKE) security-code-scan-trivy

security-image-scan: ## Run image security scans only
	@$(MAKE) backend-security-image-scan
	@$(MAKE) frontend-security-image-scan

security-code-scan-semgrep:
	@echo "Running Semgrep security scan..."
	@docker run \
		--rm \
		-v "$(PWD):/src" \
		-w /src \
		$$(grep -E '^FROM semgrep/semgrep:' docker/semgrep/Dockerfile | sed 's/^FROM //') \
		semgrep \
		--config p/ci \
		--config p/command-injection \
		--config p/cwe-top-25 \
		--config p/default \
		--config p/django \
		--config p/docker \
		--config p/docker-compose \
		--config p/dockerfile \
		--config p/javascript \
		--config p/nextjs \
		--config p/nginx \
		--config p/nodejs \
		--config p/owasp-top-ten \
		--config p/python \
		--config p/r2c-security-audit \
		--config p/react \
		--config p/secrets \
		--config p/secure-defaults \
		--config p/security-audit \
		--config p/security-headers \
		--config p/sql-injection \
		--config p/terraform \
		--config p/typescript \
		--error \
		--skip-unknown-extensions \
		--timeout 10 \
		--timeout-threshold 3 \
		--text \
		--text-output=semgrep-security-report.txt \
		.

security-code-scan-trivy:
	@echo "Running Trivy security scan..."
	@docker run \
		--rm \
		-v $(CURDIR):/src \
		-v $(CURDIR)/.trivyignore.yaml:/.trivyignore.yaml:ro \
		-v $(CURDIR)/.trivy.yaml:/.trivy.yaml:ro \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		fs --config /.trivy.yaml /src

ZAP_TARGET ?= https://nest.owasp.dev

security-scan-zap:
	@echo "Running ZAP baseline scan against $(ZAP_TARGET)..."
	@docker run \
		--rm \
		-v "$(CURDIR):/zap/wrk:rw" \
		$$(grep -E '^FROM zaproxy/zap-stable:' docker/zap/Dockerfile | sed 's/^FROM //') \
		zap-baseline.py \
		-a \
		-c .zapconfig \
		-t "$(ZAP_TARGET)"

tooling-dependency-audit:
	@echo "Auditing root tooling npm dependencies..."
	@$(MAKE) code-checks CMD='pnpm audit --audit-level=high'
