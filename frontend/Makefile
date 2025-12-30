SHELL := /bin/bash

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

shell-frontend:
	@CMD="/bin/sh" $(MAKE) exec-frontend-command-it

test-frontend: \
	test-frontend-unit \
	test-frontend-e2e

test-frontend-e2e:
	@docker container rm -f e2e-nest-db >/dev/null 2>&1 || true
	@docker volume rm -f nest-e2e_e2e-db-data >/dev/null 2>&1 || true
	@DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-e2e -f docker-compose/e2e.yaml up --build --remove-orphans --abort-on-container-exit db cache backend data-loader
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local \
	docker compose --project-name nest-e2e -f docker-compose/e2e.yaml up --build --remove-orphans --abort-on-container-exit db cache backend e2e-tests


test-frontend-unit:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build \
		--cache-from nest-test-frontend-unit \
		-f frontend/docker/Dockerfile.unit.test frontend \
		-t nest-test-frontend-unit
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-unit pnpm run test:unit

update-frontend-dependencies:
	cd frontend && pnpm update
