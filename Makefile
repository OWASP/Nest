include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile

.PHONY: build clean check pre-commit prune run scan-images security-scan test update

MAKEFLAGS += --no-print-directory

build:
	@docker compose build

clean: \
	clean-dependencies \
	clean-docker

clean-dependencies: \
	clean-backend-dependencies \
	clean-frontend-dependencies

clean-docker: \
	clean-backend-docker \
	clean-docs-docker \
	clean-frontend-docker

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
	@docker run --rm \
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

security-scan-code-trivy:
	@echo "Running Trivy security scan..."
	@docker run \
		--rm \
		-v "$(PWD):/src" \
		-v trivy-cache:/root/.cache/trivy \
		-w /src \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		fs \
		--config trivy.yaml
			.

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
