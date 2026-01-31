SHELL := /bin/bash

build-frontend-local-image:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build \
		--no-cache \
		-f docker/frontend/Dockerfile \
		-t nest-frontend-local \
		frontend

check-frontend: \
	format-frontend-code \
	lint-frontend-code \
	generate-graphql-types

clean-frontend-dependencies:
	@rm -rf frontend/.next
	@rm -rf frontend/.pnpm-store
	@rm -rf frontend/node_modules

clean-frontend-docker:
	@docker container rm -f nest-frontend >/dev/null 2>&1 || true
	@docker image rm -f nest-local-frontend >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_frontend-next >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_frontend-node-modules >/dev/null 2>&1 || true

exec-frontend-command:
	@docker exec -t nest-frontend $(CMD)

exec-frontend-command-it:
	@docker exec -it nest-frontend $(CMD)

format-frontend-code:
	@(cd frontend && (pnpm list prettier --depth=0 | grep -q 'prettier' || pnpm add -D prettier >/dev/null 2>&1) \
	  && pnpm run format:check >/dev/null 2>&1 \
	  && (printf "pnpm run format"; for i in $$(seq 1 58); do printf "."; done; printf "\033[30;42mPassed\033[0m\n") \
	  || (printf "pnpm run format"; for i in $$(seq 1 58); do printf "."; done; printf "\033[37;41mFailed\033[0m\n" && pnpm run format))

graphql-codegen:
	@cd frontend && pnpm run graphql-codegen

init-e2e-db:
	@docker container rm -f e2e-nest-db >/dev/null 2>&1 || true
	@docker volume rm -f nest-e2e_e2e-db-data >/dev/null 2>&1 || true
	@DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-e2e -f docker-compose/e2e/compose.yaml up --build --remove-orphans --abort-on-container-exit db cache backend data-loader

lighthouse-ci:
	@cd frontend && pnpm run lighthouse-ci

lighthouse-ci-desktop:
	@cd frontend && pnpm run lighthouse-ci:desktop

lint-frontend-code:
	@(cd frontend && (pnpm list eslint --depth=0 | grep -q 'eslint' || pnpm add -D eslint >/dev/null 2>&1) \
	  && pnpm run lint:check >/dev/null 2>&1 \
	  && (printf "pnpm run lint"; for i in $$(seq 1 60); do printf "."; done; printf "\033[30;42mPassed\033[0m\n") \
	  || (printf "pnpm run lint"; for i in $$(seq 1 60); do printf "."; done; printf "\033[37;41mFailed\033[0m\n" && pnpm run lint))

generate-graphql-types:
	@(cd frontend && pnpm run graphql-codegen >/dev/null 2>&1 \
	&& (printf "pnpm run graphql-codegen"; for i in $$(seq 1 49); do printf "."; done; printf "\033[30;42mPassed\033[0m\n") \
	|| (printf "pnpm run graphql-codegen"; for i in $$(seq 1 49); do printf "."; done; printf "\033[37;41mFailed\033[0m\n" \
		&& pnpm run graphql-codegen))

security-scan-frontend-image: build-frontend-local-image
	@trivy image \
		--config trivy.yaml \
		--docker-host $$(docker context inspect --format '{{.Endpoints.docker.Host}}' 2>/dev/null) \
		--exit-code 1 \
		--severity CRITICAL,HIGH \
		nest-frontend-local

shell-frontend:
	@CMD="/bin/sh" $(MAKE) exec-frontend-command-it

test-frontend: \
	test-frontend-unit \
	test-frontend-a11y \
	test-frontend-e2e

test-frontend-a11y:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build \
		--cache-from nest-test-frontend-a11y \
		-f docker/frontend/Dockerfile.a11y.test frontend \
		-t nest-test-frontend-a11y
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-a11y pnpm run test:a11y

test-frontend-e2e-no-init:
	@DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-e2e -f docker-compose/e2e/compose.yaml up --build --remove-orphans --abort-on-container-exit db cache backend frontend e2e-tests

test-frontend-e2e: init-e2e-db test-frontend-e2e-no-init

test-frontend-e2e-ui-no-init:
	@DOCKER_BUILDKIT=1 E2E_TEST_COMMAND="npx playwright test --ui-host=0.0.0.0 --ui-port=3800" \
	docker compose --project-name nest-e2e -f docker-compose/e2e/compose.yaml up --build --remove-orphans --abort-on-container-exit db cache backend frontend e2e-tests

test-frontend-e2e-ui: init-e2e-db test-frontend-e2e-ui-no-init

test-frontend-unit:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build \
		--cache-from nest-test-frontend-unit \
		-f docker/frontend/Dockerfile.unit.test frontend \
		-t nest-test-frontend-unit
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-unit pnpm run test:unit

update-frontend-dependencies:
	cd frontend && pnpm update
