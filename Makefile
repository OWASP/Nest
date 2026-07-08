include backend/Makefile
include cspell/Makefile
include docs/Makefile
include e2e/Makefile
include frontend/Makefile
include infrastructure/Makefile

.DEFAULT_GOAL := help

.PHONY: audit-backend-dependencies audit-cspell-dependencies audit-docs-dependencies \
	audit-dependencies audit-e2e-dependencies audit-frontend-dependencies audit-tooling-dependencies build check cspell \
	check-graphql clean clean-tooling-dependencies clean-trivy-cache eslint fix-eslint fix-prettier graphql-codegen help install-frontend-dependencies install-tooling-dependencies pre-commit prettier prune run \
	scan-images security-scan security-scan-backend-image security-scan-code security-scan-code-semgrep \
	security-scan-code-trivy security-scan-frontend-image security-scan-images security-scan-zap test \
	test-infrastructure test-nest-app update update-tooling-dependencies

AUDIT_LEVEL ?= high

MAKEFLAGS += --no-print-directory

##@ Getting Started

help: ## Display this help
	@[ -t 1 ] && c='\033[36m' r='\033[0m' b='\033[1m' || c='' r='' b=''; \
	awk -v c="$$c" -v r="$$r" -v b="$$b" ' \
	BEGIN { FS = ":.*##"; printf "\nUsage:\n  make " c "<target>" r "\n" } \
	/^##@/ { printf "\n" b "%s" r "\n", substr($$0, 5) } \
	/^[a-zA-Z_-]+:.*?## / { printf "  " c "%-30s" r " %s\n", $$1, $$2 }' \
	$(MAKEFILE_LIST)

build: ## Build Docker images
	@docker compose build

run: ## Run Nest application locally
	@DOCKER_BUILDKIT=1 \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local build && \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local up --remove-orphans

##@ Testing

check: ## Run all code quality checks
	@echo "================================== pre-commit =================================="
	@$(MAKE) pre-commit
	@echo ""
	@echo "=================================== prettier ==================================="
	@$(MAKE) prettier
	@echo ""
	@echo "==================================== eslint ===================================="
	@$(MAKE) eslint
	@echo ""
	@echo "==================================== cspell ===================================="
	@$(MAKE) cspell
	@echo ""

check-test: ## Run all checks and tests
check-test: \
	check \
	test

##@ Prettier

prettier: install-tooling-dependencies install-frontend-dependencies ## Verify Prettier formatting
	@pnpm run format:check && echo "Prettier: all matched files use Prettier code style."

fix-prettier: install-tooling-dependencies install-frontend-dependencies ## Auto-fix Prettier formatting
	@pnpm run format

##@ ESLint

eslint: install-tooling-dependencies install-frontend-dependencies ## Verify ESLint for e2e and frontend
	@pnpm run lint:check && echo "ESLint: no issues found."

fix-eslint: install-tooling-dependencies install-frontend-dependencies ## Auto-fix ESLint issues
	@pnpm run lint

##@ GraphQL

graphql-codegen: install-frontend-dependencies ## Regenerate GraphQL types (requires backend on PUBLIC_API_URL)
	@cd frontend && pnpm run graphql-codegen

check-graphql: install-frontend-dependencies ## Verify committed GraphQL types match backend schema (requires backend on PUBLIC_API_URL)
	@log=$$(mktemp); \
	if cd frontend && node_modules/.bin/graphql-codegen --config graphql-codegen.ts >"$$log" 2>&1; then \
		if git diff --quiet -- frontend/src/types/__generated__; then \
			echo "GraphQL types: up to date."; \
		else \
			echo "GraphQL types: out of date."; \
			git --no-pager diff -- frontend/src/types/__generated__; \
			rm -f "$$log"; \
			exit 1; \
		fi; \
	else \
		cat "$$log"; \
		rm -f "$$log"; \
		exit 1; \
	fi; \
	rm -f "$$log"

install-tooling-dependencies:
	@pnpm install --frozen-lockfile --prefer-offline >/dev/null 2>&1 \
	  || pnpm install --prefer-offline

audit-tooling-dependencies: ## Audit root lint/format npm dependencies
	@echo "Auditing root tooling npm dependencies..."
	@pnpm audit --audit-level=$(AUDIT_LEVEL)

update-tooling-dependencies:
	@pnpm update

pre-commit: ## Run pre-commit hooks
	@pre-commit run --all-files --color=always --show-diff-on-failure

test: ## Run all tests
test: \
	test-nest-app

test-nest-app:
	@$(MAKE) test-backend
	@$(MAKE) test-frontend
	@$(MAKE) test-e2e
	@$(MAKE) test-infrastructure

##@ Security

audit-dependencies: ## Audit all project dependencies for known vulnerabilities
audit-dependencies: \
	audit-backend-dependencies \
	audit-cspell-dependencies \
	audit-docs-dependencies \
	audit-e2e-dependencies \
	audit-frontend-dependencies \
	audit-tooling-dependencies

security-scan: ## Run all security scans
security-scan: \
	security-scan-code \
	security-scan-images

security-scan-code: ## Run code security scans only
security-scan-code: \
	security-scan-code-semgrep \
	security-scan-code-trivy

security-scan-images: ## Run image security scans only
security-scan-images: \
	security-scan-backend-image \
	security-scan-frontend-image

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
		-t $(ZAP_TARGET)

##@ Cleanup

clean: ## Remove all generated files and containers
clean: \
	clean-dependencies \
	clean-docker \
	clean-trivy-cache

clean-dependencies: \
	clean-backend-dependencies \
	clean-frontend-dependencies \
	clean-tooling-dependencies

clean-tooling-dependencies:
	@rm -rf node_modules

clean-docker: \
	clean-backend-docker \
	clean-docs-docker \
	clean-frontend-docker

clean-trivy-cache:
	@rm -rf $(CURDIR)/.trivy-cache

prune: ## Prune Docker resources
	@docker builder prune --filter 'until=72h' -a -f
	@docker image prune --filter 'until=72h' -a -f
	@docker volume prune -f

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
	update-frontend-dependencies \
	update-tooling-dependencies

update-pre-commit:
	@pre-commit autoupdate
