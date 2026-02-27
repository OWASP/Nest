include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile
include infrastructure/Makefile

.DEFAULT_GOAL := help

.PHONY: build clean check pre-commit prune run scan-images security-scan security-scan-code \
	security-scan-code-semgrep security-scan-code-trivy security-scan-images \
	security-scan-backend-image security-scan-frontend-image security-scan-zap \
	test update clean-trivy-cache help

MAKEFLAGS += --no-print-directory

##@ Getting Started
build: ## Build Docker images
	@docker compose build

run: ## Run Nest application locally
	@DOCKER_BUILDKIT=1 \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local build && \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local up --remove-orphans

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } \
		/^[a-zA-Z_-]+:.*?## / { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 }' \
		$(MAKEFILE_LIST)

##@ Cleanup
clean: ## Remove all generated files and containers
clean: \
	clean-dependencies \
	clean-docker \
	clean-trivy-cache

clean-dependencies: \
	clean-backend-dependencies \
	clean-frontend-dependencies

clean-docker: \
	clean-backend-docker \
	clean-docs-docker \
	clean-frontend-docker

clean-trivy-cache: ## Remove Trivy cache
	@rm -rf $(CURDIR)/.trivy-cache

prune: ## Prune Docker resources older than 72h
	@docker builder prune --filter 'until=72h' -a -f
	@docker image prune --filter 'until=72h' -a -f
	@docker volume prune -f

##@ Testing
check: ## Run all code quality checks
check: \
	check-spelling \
	check-backend \
	check-frontend

check-backend: \
	pre-commit

check-test: ## Run all checks and tests
check-test: \
	check \
	test

check-test-backend: \
	pre-commit \
	test-backend

check-test-frontend: \
	check-frontend \
	test-frontend

test: ## Run all tests
test: \
	test-nest-app

test-nest-app: \
	test-backend \
	test-frontend

pre-commit: ## Run pre-commit hooks
	@pre-commit run -a

##@ Security
security-scan: ## Run all security scans
security-scan: \
	security-scan-code \
	security-scan-images

security-scan-code: ## Run code security scans
security-scan-code: \
	security-scan-code-semgrep \
	security-scan-code-trivy

security-scan-images: ## Run image security scans
security-scan-images: \
	security-scan-backend-image \
	security-scan-frontend-image

security-scan-code-semgrep: ## Run Semgrep security scan
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

SCANNERS ?= misconfig,vuln

security-scan-code-trivy: ## Run Trivy security scan
	@echo "Running Trivy security scan..."
	@docker run \
		--rm \
		-e TRIVY_SCANNERS="$(SCANNERS)" \
		-v $(CURDIR):/src \
		-v $(CURDIR)/trivyignore.yaml:/trivyignore.yaml:ro \
		-v $(CURDIR)/trivy.yaml:/trivy.yaml:ro \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		fs --config /trivy.yaml /src

ZAP_TARGET ?= https://nest.owasp.dev

security-scan-zap: ## Run ZAP baseline scan
	@echo "Running ZAP baseline scan against $(ZAP_TARGET)..."
	@docker run \
		--rm \
		-v "$(CURDIR):/zap/wrk:rw" \
		$$(grep -E '^FROM zaproxy/zap-stable:' docker/zap/Dockerfile | sed 's/^FROM //') \
		zap-baseline.py \
		-a \
		-c .zapconfig \
		-t $(ZAP_TARGET)

##@ Maintenance
update: ## Update all dependencies
update: \
	clean-dependencies \
	update-docs-dependencies \
	update-nest-app-dependencies \
	update-pre-commit

update-nest-app-dependencies: \
	update-backend-dependencies \
	update-cspell-dependencies \
	update-frontend-dependencies

update-pre-commit:
	@pre-commit autoupdate
