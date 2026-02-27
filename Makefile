include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile
include infrastructure/Makefile

.PHONY: build clean check pre-commit prune run scan-images security-scan security-scan-code \
	security-scan-code-semgrep security-scan-code-trivy security-scan-images \
	security-scan-backend-image security-scan-frontend-image security-scan-zap \
	test update clean-trivy-cache

MAKEFLAGS += --no-print-directory
.DEFAULT_GOAL := help

##@ Getting Started

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } \
		/^[a-zA-Z0-9_-]+:.*?## / { printf "  \033[36m%-30s\033[0m%s\n", $$1, $$2 }' \
		$(MAKEFILE_LIST)
	@echo ""

run: ## Start the application locally
	@DOCKER_BUILDKIT=1 \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local build && \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local up --remove-orphans

build: ## Build all Docker images
	@docker compose build

##@ Cleanup & Maintenance

clean: clean-dependencies clean-docker clean-trivy-cache ## Remove all build artifacts

clean-dependencies: \
	clean-backend-dependencies \
	clean-frontend-dependencies

clean-docker: \
	clean-backend-docker \
	clean-docs-docker \
	clean-frontend-docker

clean-trivy-cache:
	@rm -rf $(CURDIR)/.trivy-cache

##@ Code Quality

check: check-spelling check-backend check-frontend ## Run all code quality checks

check-backend: \
	pre-commit

check-test: check test \ ## Run all checks and tests

check-test-backend: \
	pre-commit \
	test-backend

check-test-frontend: \
	check-frontend \
	test-frontend

pre-commit: ## Run pre-commit hooks
	@pre-commit run -a

prune: ## Prune Docker resources older than 72h
	@docker builder prune --filter 'until=72h' -a -f
	@docker image prune --filter 'until=72h' -a -f
	@docker volume prune -f

##@ Security

security-scan: security-scan-code security-scan-images ## Run all security scans (code + images)

security-scan-code: security-scan-code-semgrep security-scan-code-trivy ## Run code security scans only

security-scan-images: security-scan-backend-image security-scan-frontend-image ## Run image security scans only

security-scan-code-semgrep:
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

security-scan-code-trivy:
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

security-scan-zap:
	@echo "Running ZAP baseline scan against $(ZAP_TARGET)..."
	@docker run \
		--rm \
		-v "$(CURDIR):/zap/wrk:rw" \
		$$(grep -E '^FROM zaproxy/zap-stable:' docker/zap/Dockerfile | sed 's/^FROM //') \
		zap-baseline.py \
		-a \
		-c .zapconfig \
		-t $(ZAP_TARGET)

##@ Testing

test: test-nest-app ## Run all tests (backend + frontend)

test-nest-app: \
	test-backend \
	test-frontend

update: clean-dependencies update-docs-dependencies update-nest-app-dependencies update-pre-commit ## Update all dependencies

update-nest-app-dependencies: \
	update-backend-dependencies \
	update-cspell-dependencies \
	update-frontend-dependencies

update-pre-commit:
	@pre-commit autoupdate
