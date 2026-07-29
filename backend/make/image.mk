.PHONY: backend-image-build backend-image-sbom

BACKEND_IMAGE_NAME ?= nest-backend-local
SBOM_VERSION := $(if $(RELEASE_VERSION),$(RELEASE_VERSION),local)

backend-image-build:
	@DOCKER_BUILDKIT=1 docker build \
		--no-cache \
		--target backend \
		-f docker/backend/Dockerfile \
		-t nest-backend-local \
		backend

backend-image-sbom:
	@if [ "$(BACKEND_IMAGE_NAME)" = "nest-backend-local" ]; then \
		$(MAKE) backend-image-build; \
	fi
	@echo "Generating SBOM for image: $(BACKEND_IMAGE_NAME)..."
	@docker run \
		--rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		-v $(CURDIR):/work \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		image \
		--format cyclonedx \
		--output /work/backend-sbom-$(SBOM_VERSION).cdx.json \
		$(BACKEND_IMAGE_NAME)
