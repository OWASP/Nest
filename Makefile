include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile

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

scan-images: \
	scan-backend-image \
	scan-frontend-image

security-scan:
	@echo "Running Security Scan..."
	@docker run --rm \
		-v "$(PWD):/src" \
		-w /src \
		$$(grep -E '^FROM semgrep/semgrep:' docker/semgrep/Dockerfile | sed 's/^FROM //') \
		semgrep \
			--config p/ci \
			--config p/javascript \
			--config p/nginx \
			--config p/owasp-top-ten \
			--config p/python \
			--config p/secrets \
			--config p/security-audit \
			--config p/sql-injection \
			--config p/typescript \
			--error \
			--skip-unknown-extensions \
			--timeout 10 \
			--timeout-threshold 3 \
			--text \
			--text-output=semgrep-security-report.txt \
			.

security-scan-deps:
	@echo "Running Trivy Filesystem Scan..."
	@docker run --rm \
		-v "$(PWD):/src" \
		-w /src \
		aquasec/trivy fs \
			--config trivy.yaml \
			.

security-scan-repo:
	@echo "Running Trivy Repository Scan..."
	@docker run --rm \
		-v "$(PWD):/src" \
		-w /src \
		aquasec/trivy repo \
			--config trivy.yaml \
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

.PHONY: build clean check pre-commit prune run scan-images security-scan security-scan-deps security-scan-repo test update
