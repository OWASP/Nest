include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile
include infrastructure/Makefile

HELP_MAKEFILES := $(shell find . -name Makefile -print | sort)

.PHONY: build clean check pre-commit prune run scan-images security-scan security-scan-code \
	security-scan-code-semgrep security-scan-code-trivy security-scan-images \
	security-scan-backend-image security-scan-frontend-image security-scan-zap \
	test update clean-trivy-cache help

MAKEFLAGS += --no-print-directory

build: ## @Getting started Build container images
	@docker compose build

## @Cleanup Remove build artifacts, containers, and caches
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

clean-trivy-cache: ## @Cleanup Remove Trivy cache
	@rm -rf $(CURDIR)/.trivy-cache

## @Testing Run linting and static checks
check: \
	check-spelling \
	check-backend \
	check-frontend

check-backend: \
	pre-commit

## @Testing Run checks and tests
check-test: \
	check \
	test

check-test-backend: \
	pre-commit \
	test-backend

check-test-frontend: \
	check-frontend \
	test-frontend

pre-commit: ## @Testing Run all pre-commit hooks
	@pre-commit run -a

prune: ## @Cleanup Prune unused Docker resources
	@docker builder prune --filter 'until=72h' -a -f
	@docker image prune --filter 'until=72h' -a -f
	@docker volume prune -f

run: ## @Getting started Run the app locally
	@DOCKER_BUILDKIT=1 \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local build && \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local up --remove-orphans

## @Security Run all security scans
security-scan: \
	security-scan-code \
	security-scan-images

## @Security Run code security scans
security-scan-code: \
	security-scan-code-semgrep \
	security-scan-code-trivy

## @Security Run image security scans
security-scan-images: \
	security-scan-backend-image \
	security-scan-frontend-image

security-scan-code-semgrep: ## @Security Run Semgrep security scan
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

security-scan-code-trivy: ## @Security Run Trivy security scan
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

security-scan-zap: ## @Security Run ZAP baseline scan
	@echo "Running ZAP baseline scan against $(ZAP_TARGET)..."
	@docker run \
		--rm \
		-v "$(CURDIR):/zap/wrk:rw" \
		$$(grep -E '^FROM zaproxy/zap-stable:' docker/zap/Dockerfile | sed 's/^FROM //') \
		zap-baseline.py \
		-a \
		-c .zapconfig \
		-t $(ZAP_TARGET)

## @Testing Run all tests
test: \
	test-nest-app

test-nest-app: \
	test-backend \
	test-frontend

## @Maintenance Update dependencies
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

help: ## @Help Show this help
	@printf "Usage: make <target>\n\n"
	@awk ' \
	function add_entry(target, desc) { \
		cat="Other"; \
		if (desc ~ /^@/) { \
			parts_count=split(desc, parts, " "); \
			cat=substr(parts[1], 2); \
			start=2; \
			if (parts_count >= 2 && parts[2] ~ /^[a-z]/) { \
				cat=cat " " parts[2]; \
				start=3; \
			} \
			desc=""; \
			for (i=start; i<=parts_count; i++) { \
				desc=desc (desc=="" ? "" : " ") parts[i]; \
			} \
			if (desc=="") { desc=cat; } \
		} \
		if (!(cat in seen)) { order[++n]=cat; seen[cat]=1; } \
		entries[cat]=entries[cat] sprintf("  %-28s %s\n", target, desc); \
	} \
	BEGIN { doc=""; } \
	/^## / { doc=substr($$0, 4); next; } \
	/^[a-zA-Z0-9][^$$#:=]*:.*## / { \
		split($$0, parts, /:.*## /); \
		add_entry(parts[1], parts[2]); \
		doc=""; \
		next; \
	} \
	/^[a-zA-Z0-9][^$$#:=]*:/ { \
		if (doc != "") { \
			split($$0, parts, ":"); \
			add_entry(parts[1], doc); \
			doc=""; \
		} \
	} \
	END { \
		print "Available targets:"; \
		for (i=1; i<=n; i++) { \
			cat=order[i]; \
			print ""; \
			print cat ":"; \
			printf "%s", entries[cat]; \
		} \
	}' $(HELP_MAKEFILES)
