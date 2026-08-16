.PHONY: frontend-image-build frontend-image-sbom

FRONTEND_IMAGE_NAME ?= nest-frontend-local
SBOM_VERSION := $(if $(RELEASE_VERSION),$(RELEASE_VERSION),local)

frontend-image-build:
	@DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build \
	    --build-arg FORCE_STANDALONE=yes \
	    --no-cache \
	    -f docker/frontend/Dockerfile \
	    -t nest-frontend-local \
	    frontend

frontend-image-sbom:
	@if [ "$(FRONTEND_IMAGE_NAME)" = "nest-frontend-local" ]; then \
		$(MAKE) frontend-image-build; \
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
