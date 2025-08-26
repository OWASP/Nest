SHELL := /bin/bash

check-frontend: \
	format-frontend-code \
	lint-frontend-code

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
	@(cd frontend && pnpm run format:check >/dev/null 2>&1 \
	&& (printf "pnpm run format"; for i in $$(seq 1 58); do printf "."; done; printf "\033[30;42mPassed\033[0m\n") \
	|| (printf "pnpm run format"; for i in $$(seq 1 58); do printf "."; done; printf "\033[37;41mFailed\033[0m\n" \
		&& pnpm run format))

lighthouse-ci:
	@cd frontend && pnpm run lighthouse-ci

lighthouse-ci-desktop:
	@cd frontend && pnpm run lighthouse-ci:desktop

lint-frontend-code:
	@(cd frontend && pnpm run lint:check >/dev/null 2>&1 \
	&& (printf "pnpm run lint"; for i in $$(seq 1 60); do printf "."; done; printf "\033[30;42mPassed\033[0m\n") \
	|| (printf "pnpm run lint"; for i in $$(seq 1 60); do printf "."; done; printf "\033[37;41mFailed\033[0m\n" \
		&& pnpm run lint))

shell-frontend:
	@CMD="/bin/sh" $(MAKE) exec-frontend-command-it

test-frontend: \
	test-frontend-unit \
	test-frontend-e2e

test-frontend-e2e:
	@DOCKER_BUILDKIT=1 docker build \
		--cache-from nest-test-frontend-e2e \
		-f frontend/docker/Dockerfile.e2e.test frontend \
		-t nest-test-frontend-e2e
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-e2e pnpm run test:e2e

test-frontend-unit:
	@DOCKER_BUILDKIT=1 docker build \
		--cache-from nest-test-frontend-unit \
		-f frontend/docker/Dockerfile.unit.test frontend \
		-t nest-test-frontend-unit
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-unit pnpm run test:unit

update-frontend-dependencies:
	cd frontend && pnpm update
