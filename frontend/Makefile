SHELL := /bin/bash

.PHONY: sbom-frontend-image

build-frontend-local-image:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build \
	    --build-arg FORCE_STANDALONE=yes \
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

FRONTEND_IMAGE_NAME ?= nest-frontend-local
IMAGE_SCANNERS ?= misconfig,secret,vuln

security-scan-frontend-image:
	@if [ "$(FRONTEND_IMAGE_NAME)" = "nest-frontend-local" ]; then \
		$(MAKE) build-frontend-local-image; \
	fi
	@echo "Scanning image: $(FRONTEND_IMAGE_NAME)..."
	@docker run \
		--rm \
		-e TRIVY_SCANNERS="$(IMAGE_SCANNERS)" \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/trivy.yaml:/trivy.yaml:ro \
		-v $(CURDIR)/trivyignore.yaml:/trivyignore.yaml:ro \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		image --config /trivy.yaml $(FRONTEND_IMAGE_NAME)

SBOM_VERSION := $(if $(RELEASE_VERSION),$(RELEASE_VERSION),local)

sbom-frontend-image:
	@if [ "$(FRONTEND_IMAGE_NAME)" = "nest-frontend-local" ]; then \
		$(MAKE) build-frontend-local-image; \
	fi
	@echo "Generating SBOM for image: $(FRONTEND_IMAGE_NAME)..."
	@docker run \
		--rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR):/work \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		image \
		--format cyclonedx \
		--output /work/frontend-sbom-$(SBOM_VERSION).cdx.json \
		$(FRONTEND_IMAGE_NAME)

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

test-frontend-e2e:
	@docker container rm -f e2e-nest-db >/dev/null 2>&1 || true
	@docker volume rm -f nest-e2e_e2e-db-data >/dev/null 2>&1 || true
	@DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-e2e -f docker-compose/e2e/compose.yaml up --build --remove-orphans --abort-on-container-exit db cache backend data-loader
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local \
	docker compose --project-name nest-e2e -f docker-compose/e2e/compose.yaml up --build --remove-orphans --abort-on-container-exit db cache backend e2e-tests

test-frontend-unit:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build \
		--cache-from nest-test-frontend-unit \
		-f docker/frontend/Dockerfile.unit.test frontend \
		-t nest-test-frontend-unit
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-unit pnpm run test:unit

update-frontend-dependencies:
	cd frontend && pnpm update
