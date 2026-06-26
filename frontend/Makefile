.PHONY: audit-frontend-dependencies install-frontend-dependencies sbom-frontend-image

##@ Frontend

build-frontend-local-image:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build \
	    --build-arg FORCE_STANDALONE=yes \
	    --no-cache \
	    -f docker/frontend/Dockerfile \
	    -t nest-frontend-local \
	    frontend

install-frontend-dependencies:
	@(cd frontend && (pnpm install --frozen-lockfile --prefer-offline >/dev/null 2>&1 \
	  || pnpm install --prefer-offline))

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

lighthouse-ci:
	@cd frontend && pnpm run lighthouse-ci

lighthouse-ci-desktop:
	@cd frontend && pnpm run lighthouse-ci:desktop

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
		-v $(CURDIR)/.trivy.yaml:/.trivy.yaml:ro \
		-v $(CURDIR)/.trivyignore.yaml:/.trivyignore.yaml:ro \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		image --config /.trivy.yaml $(FRONTEND_IMAGE_NAME)

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

test-frontend: ## Run all frontend tests
test-frontend: \
	test-frontend-unit \
	test-frontend-a11y

test-frontend-a11y:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build -q \
		--cache-from nest-test-frontend-a11y \
		-f docker/frontend/Dockerfile.a11y-tests frontend \
		-t nest-test-frontend-a11y 1>/dev/null
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-a11y pnpm run test:a11y

test-frontend-unit:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build -q \
		--cache-from nest-test-frontend-unit \
		-f docker/frontend/Dockerfile.unit-tests frontend \
		-t nest-test-frontend-unit 1>/dev/null
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-unit pnpm run test:unit

audit-frontend-dependencies: ## Audit frontend npm dependencies
	@echo "Auditing frontend npm dependencies..."
	@cd frontend && pnpm audit --audit-level=$(AUDIT_LEVEL)

update-frontend-dependencies:
	cd frontend && pnpm update
