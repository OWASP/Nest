.PHONY: backend-image-build backend-image-sbom backend-image-maybe-build-local

BACKEND_IMAGE_NAME ?= nest-backend-local
SBOM_VERSION := $(if $(RELEASE_VERSION),$(RELEASE_VERSION),local)

backend-image-build:
	@args=(
		'--no-cache'
		'--target=backend'
		'-f=docker/backend/Dockerfile'
		'-t=nest-backend-local'
		backend
	)
	DOCKER_BUILDKIT=1 docker build "$${args[@]}"

# Keep $(MAKE) out of the SBOM recipe so `make -n` does not run docker under .ONESHELL.
backend-image-maybe-build-local:
	@if [ "$(BACKEND_IMAGE_NAME)" = "nest-backend-local" ]; then
		$(MAKE) backend-image-build
	fi

backend-image-sbom: backend-image-maybe-build-local
	@echo "Generating SBOM for image: $(BACKEND_IMAGE_NAME)..."
	image="$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //')"
	args=(
		'--rm'
		'-v=/var/run/docker.sock:/var/run/docker.sock'
		'-v=$(CURDIR)/.trivy-cache:/root/.cache/trivy'
		'-v=$(CURDIR):/work'
		"$$image"
		image
		'--format=cyclonedx'
		'--output=/work/backend-sbom-$(SBOM_VERSION).cdx.json'
		$(BACKEND_IMAGE_NAME)
	)
	docker run "$${args[@]}"
