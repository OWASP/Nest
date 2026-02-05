include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile

.PHONY: build clean check pre-commit prune run scan-images security-scan security-scan-code \
	security-scan-code-semgrep security-scan-code-trivy security-scan-images \
	security-scan-backend-image security-scan-frontend-image test update \
	clean-trivy-cache validate-compose

.ONESHELL: validate-compose

MAKEFLAGS += --no-print-directory

build:
	@docker compose build

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

clean-trivy-cache:
	@rm -rf $(CURDIR)/.trivy-cache

check: \
	check-spelling \
	check-backend \
	check-frontend

check-backend: \
	pre-commit

check-test: \
	check \
	test

check-test-backend: \
	pre-commit \
	test-backend

check-test-frontend: \
	check-frontend \
	test-frontend

pre-commit:
	@pre-commit run -a

prune:
	@docker builder prune --filter 'until=72h' -a -f
	@docker image prune --filter 'until=72h' -a -f
	@docker volume prune -f

run:
	@DOCKER_BUILDKIT=1 \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local build && \
	docker compose -f docker-compose/local/compose.yaml --project-name nest-local up --remove-orphans

ENV_FILES := .env.backend .env.cache .env.db .env.frontend

validate-compose:
	@set -eu
	@files_to_clean=""
	# cleanup any placeholders we create
	@trap 'if [ -n "$$files_to_clean" ]; then rm -f $$files_to_clean; fi' EXIT
	# ensure production/staging env files exist for validation
	@for dir in production staging; do
		@for env_file in $(ENV_FILES); do
			@path="docker-compose/$$dir/$$env_file"
			@if [ ! -f "$$path" ]; then
				@touch "$$path"
				@files_to_clean="$$files_to_clean $$path"
			@fi
		@done
	@done
	# validate all compose files
	@for file in docker-compose/*/compose.yaml; do
		@echo "Validating $$file..."
		@docker compose -f "$$file" config --quiet
	@done
	@echo "✅ All compose files are valid!"

security-scan: \
	security-scan-code \
	security-scan-images

security-scan-code: \
	security-scan-code-semgrep \
	security-scan-code-trivy

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
		-v $(CURDIR)/trivyignore.yaml:/trivyignore.yaml:ro \
		-v $(CURDIR)/trivy.yaml:/trivy.yaml:ro \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		fs --config /trivy.yaml /src

test: \
	test-nest-app

test-nest-app: \
	test-backend \
	test-frontend

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
