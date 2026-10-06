.PHONY: test-frontend frontend-test frontend-test-a11y frontend-test-lighthouse-ci \
	frontend-test-lighthouse-ci-desktop frontend-test-unit

test-frontend: ## Run frontend tests
	@$(MAKE) frontend-test

# Implementation targets.

LHCI_BASE_URL ?= http://nest-frontend:3000
LHCI_NETWORK ?= nest-local_nest-network
JEST_MAX_WORKERS ?= 50%

frontend-test:
	@$(MAKE) frontend-test-unit
	@$(MAKE) frontend-test-a11y

frontend-test-a11y:
	@args=(
		'-q'
		'--cache-from=nest-test-frontend-a11y'
		'-f=docker/frontend/Dockerfile.a11y-tests'
		frontend
		'-t=nest-test-frontend-a11y'
	)
	DOCKER_BUILDKIT=1 docker build "$${args[@]}" 1>/dev/null
	args=(
		'--env-file=frontend/.env.example'
		'--rm'
		nest-test-frontend-a11y
		pnpm
		run
		test:a11y
		'--'
		'--maxWorkers=$(JEST_MAX_WORKERS)'
	)
	docker run "$${args[@]}"

frontend-test-lighthouse-ci:
	@args=(
		'-q'
		'--cache-from=nest-test-frontend-lighthouse'
		'-f=docker/frontend/Dockerfile.lighthouse'
		frontend
		'-t=nest-test-frontend-lighthouse'
	)
	DOCKER_BUILDKIT=1 docker build "$${args[@]}" 1>/dev/null
	args=(
		'--rm'
		"--env=LHCI_BASE_URL=$(LHCI_BASE_URL)"
		"--network=$(LHCI_NETWORK)"
		nest-test-frontend-lighthouse
		pnpm
		run
		lighthouse-ci
	)
	docker run "$${args[@]}"

frontend-test-lighthouse-ci-desktop:
	@args=(
		'-q'
		'--cache-from=nest-test-frontend-lighthouse'
		'-f=docker/frontend/Dockerfile.lighthouse'
		frontend
		'-t=nest-test-frontend-lighthouse'
	)
	DOCKER_BUILDKIT=1 docker build "$${args[@]}" 1>/dev/null
	args=(
		'--rm'
		"--env=LHCI_BASE_URL=$(LHCI_BASE_URL)"
		"--network=$(LHCI_NETWORK)"
		nest-test-frontend-lighthouse
		pnpm
		run
		lighthouse-ci:desktop
	)
	docker run "$${args[@]}"

frontend-test-unit:
	@args=(
		'-q'
		'--cache-from=nest-test-frontend-unit'
		'-f=docker/frontend/Dockerfile.unit-tests'
		frontend
		'-t=nest-test-frontend-unit'
	)
	DOCKER_BUILDKIT=1 docker build "$${args[@]}" 1>/dev/null
	args=(
		'--env-file=frontend/.env.example'
		'--rm'
		nest-test-frontend-unit
		pnpm
		run
		test:unit
		'--'
		'--maxWorkers=$(JEST_MAX_WORKERS)'
	)
	docker run "$${args[@]}"
