include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile

MAKEFLAGS += --no-print-directory

SEMGREP_CONFIGS := --config p/owasp-top-ten \
                   --config p/python \
                   --config p/javascript \
                   --config p/typescript \
                   --config p/sql-injection \
                   --config p/secrets \
                   --timeout 10 \
                   --timeout-threshold 3 \

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
	@echo "🛡️  Running Centralized Security Scan..."
	semgrep $(SEMGREP_CONFIGS) --error --output findings.txt .
	@echo "✅ Scan Complete. Detailed findings saved to findings.txt"

security-scan-ci:
	@echo "🛡️  Running CI Security Scan..."
	semgrep $(SEMGREP_CONFIGS) --error .

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

.PHONY: build clean check pre-commit prune run scan-images security-scan test update
