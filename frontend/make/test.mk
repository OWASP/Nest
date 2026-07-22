.PHONY: test-frontend frontend-test frontend-test-a11y frontend-test-lighthouse-ci \
	frontend-test-lighthouse-ci-desktop frontend-test-unit

test-frontend: ## Run frontend tests
	@$(MAKE) frontend-test

# Implementation targets.

LHCI_BASE_URL ?= http://nest-frontend:3000
LHCI_NETWORK ?= nest-local_nest-network
JEST_MAX_WORKERS ?= 50%
JEST_WORKER_ARGS := -- --maxWorkers=$(JEST_MAX_WORKERS)

frontend-test:
	@$(MAKE) frontend-test-unit
	@$(MAKE) frontend-test-a11y

frontend-test-a11y:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from nest-test-frontend-a11y \
		-f docker/frontend/Dockerfile.a11y-tests frontend \
		-t nest-test-frontend-a11y 1>/dev/null
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-a11y \
		pnpm run test:a11y $(JEST_WORKER_ARGS)

frontend-test-lighthouse-ci:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from nest-test-frontend-lighthouse \
		-f docker/frontend/Dockerfile.lighthouse frontend \
		-t nest-test-frontend-lighthouse 1>/dev/null
	@docker run --rm \
		--env LHCI_BASE_URL="$(LHCI_BASE_URL)" \
		--network "$(LHCI_NETWORK)" \
		nest-test-frontend-lighthouse \
		pnpm run lighthouse-ci

frontend-test-lighthouse-ci-desktop:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from nest-test-frontend-lighthouse \
		-f docker/frontend/Dockerfile.lighthouse frontend \
		-t nest-test-frontend-lighthouse 1>/dev/null
	@docker run --rm \
		--env LHCI_BASE_URL="$(LHCI_BASE_URL)" \
		--network "$(LHCI_NETWORK)" \
		nest-test-frontend-lighthouse \
		pnpm run lighthouse-ci:desktop

frontend-test-unit:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from nest-test-frontend-unit \
		-f docker/frontend/Dockerfile.unit-tests frontend \
		-t nest-test-frontend-unit 1>/dev/null
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-unit \
		pnpm run test:unit $(JEST_WORKER_ARGS)
