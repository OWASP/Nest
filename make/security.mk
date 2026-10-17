##@ Security

.PHONY: security-dependency-audit security-dependency-check security-dependency-scan \
	security-scan security-sast-scan security-dast-scan security-image-scan \
	security-repository-scan security-sast-scan-semgrep \
	security-dependency-check-osv security-dependency-check-trivy \
	security-repository-scan-trivy security-dast-scan-zap tooling-dependency-audit

security-scan: ## Run security scans
	@$(MAKE) security-sast-scan
	@$(MAKE) security-repository-scan
	@$(MAKE) security-dependency-scan
	@$(MAKE) security-image-scan
	@$(MAKE) security-dast-scan

security-dependency-audit: ## Audit dependencies for known vulnerabilities
	@exit_code=0
	echo "============================= Backend dependency audit ============================="
	$(MAKE) backend-dependency-audit || exit_code=1
	echo ""
	echo "============================= CSpell dependency audit =============================="
	$(MAKE) cspell-dependency-audit || exit_code=1
	echo ""
	echo "============================== Docs dependency audit ==============================="
	$(MAKE) docs-dependency-audit || exit_code=1
	echo ""
	echo "=============================== E2E dependency audit ==============================="
	$(MAKE) e2e-dependency-audit || exit_code=1
	echo ""
	echo "============================ Frontend dependency audit ============================="
	$(MAKE) frontend-dependency-audit || exit_code=1
	echo ""
	echo "========================= Infrastructure dependency audit =========================="
	$(MAKE) infrastructure-dependency-audit || exit_code=1
	echo ""
	echo "============================ Tooling dependency audit =============================="
	$(MAKE) tooling-dependency-audit || exit_code=1
	echo ""
	exit $$exit_code

security-dependency-scan: ## Audit and check dependencies for known vulnerabilities
	@exit_code=0
	$(MAKE) security-dependency-audit || exit_code=1
	$(MAKE) security-dependency-check || exit_code=1
	exit $$exit_code

security-dependency-check: ## Check dependencies for known vulnerabilities
	@exit_code=0
	$(MAKE) security-dependency-check-osv || exit_code=1
	$(MAKE) security-dependency-check-trivy || exit_code=1
	exit $$exit_code

security-repository-scan: ## Scan the repository for misconfigurations and secrets
	@$(MAKE) security-repository-scan-trivy

security-dast-scan: ## Run DAST security scan
	@$(MAKE) security-dast-scan-zap

security-image-scan: ## Run image security scan
	@$(MAKE) backend-security-image-scan
	@$(MAKE) frontend-security-image-scan

security-sast-scan: ## Run SAST security scan
	@$(MAKE) security-sast-scan-semgrep

security-sast-scan-semgrep:
	@echo "Running Semgrep security scan..."
	image="$$(grep -E '^FROM semgrep/semgrep:' docker/semgrep/Dockerfile | sed 's/^FROM //')"
	args=(
		'--rm'
		"-v=$(PWD):/src"
		'-w=/src'
		"$$image"
		semgrep
		'--config=p/ci'
		'--config=p/command-injection'
		'--config=p/cwe-top-25'
		'--config=p/default'
		'--config=p/django'
		'--config=p/docker'
		'--config=p/docker-compose'
		'--config=p/dockerfile'
		'--config=p/javascript'
		'--config=p/nextjs'
		'--config=p/nodejs'
		'--config=p/owasp-top-ten'
		'--config=p/python'
		'--config=p/r2c-security-audit'
		'--config=p/react'
		'--config=p/secrets'
		'--config=p/secure-defaults'
		'--config=p/security-audit'
		'--config=p/security-headers'
		'--config=p/sql-injection'
		'--config=p/terraform'
		'--config=p/typescript'
		'--error'
		'--skip-unknown-extensions'
		'--timeout=10'
		'--timeout-threshold=3'
		'--text'
		'--text-output=semgrep-security-report.txt'
		.
	)
	docker run "$${args[@]}"

security-dependency-check-trivy:
	@echo "Running Trivy vulnerability check..."
	image="$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //')"
	args=(
		'--rm'
		'-v=$(CURDIR):/src'
		'-v=$(CURDIR)/.trivyignore.yaml:/.trivyignore.yaml:ro'
		'-v=$(CURDIR)/.trivy.yaml:/.trivy.yaml:ro'
		'-v=$(CURDIR)/.trivy-cache:/root/.cache/trivy'
		"$$image"
		fs
		'--config=/.trivy.yaml'
		'--scanners=vuln'
		/src
	)
	docker run "$${args[@]}"

security-dependency-check-osv:
	@echo "Running OSV vulnerability check..."
	image="$$(grep -E '^FROM ghcr.io/google/osv-scanner:' docker/osv-scanner/Dockerfile | sed 's/^FROM //')"
	args=(
		'--rm'
		'-v=$(CURDIR):/src'
		'-v=$(CURDIR)/.osv-scanner-cache:/root/.cache/osv-scanner'
		"$$image"
		scan
		source
		'--recursive'
		/src
	)
	docker run "$${args[@]}"

security-repository-scan-trivy:
	@echo "Running Trivy repository scan..."
	image="$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //')"
	args=(
		'--rm'
		'-v=$(CURDIR):/src'
		'-v=$(CURDIR)/.trivyignore.yaml:/.trivyignore.yaml:ro'
		'-v=$(CURDIR)/.trivy.yaml:/.trivy.yaml:ro'
		'-v=$(CURDIR)/.trivy-cache:/root/.cache/trivy'
		"$$image"
		fs
		'--config=/.trivy.yaml'
		'--scanners=misconfig,secret'
		/src
	)
	docker run "$${args[@]}"

ZAP_TARGET ?= http://host.docker.internal:3000

security-dast-scan-zap:
	@echo "Running ZAP baseline scan against $(ZAP_TARGET)..."
	image="$$(grep -E '^FROM zaproxy/zap-stable:' docker/zap/Dockerfile | sed 's/^FROM //')"
	args=(
		'--add-host=host.docker.internal:host-gateway'
		'--rm'
		"-v=$(CURDIR):/zap/wrk:rw"
		"$$image"
		zap-baseline.py
		'-a'
		'-c=.zapconfig'
		"-t=$(ZAP_TARGET)"
	)
	docker run "$${args[@]}"

tooling-dependency-audit:
	@echo "Auditing root tooling npm dependencies..."
	@$(MAKE) code-checks CMD='pnpm audit --audit-level=moderate'
