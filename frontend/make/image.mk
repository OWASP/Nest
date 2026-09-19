.PHONY: frontend-image-build frontend-image-sbom frontend-image-maybe-build-local

FRONTEND_IMAGE_NAME ?= nest-frontend-local
SBOM_VERSION := $(if $(RELEASE_VERSION),$(RELEASE_VERSION),local)

frontend-image-build:
	@args=(
		'--build-arg=FORCE_STANDALONE=yes'
		'--no-cache'
		'-f=docker/frontend/Dockerfile'
		'-t=nest-frontend-local'
		frontend
	)
	DOCKER_BUILDKIT=1 NEXT_PUBLIC_ENVIRONMENT=local docker build "$${args[@]}"

# Keep $(MAKE) out of the SBOM recipe so `make -n` does not run docker under .ONESHELL.
frontend-image-maybe-build-local:
	@if [ "$(FRONTEND_IMAGE_NAME)" = "nest-frontend-local" ]; then
		$(MAKE) frontend-image-build
	fi

frontend-image-sbom: frontend-image-maybe-build-local
	@echo "Generating SBOM for image: $(FRONTEND_IMAGE_NAME)..."
	image="$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //')"
	args=(
		'--rm'
		'-v=/var/run/docker.sock:/var/run/docker.sock'
		'-v=$(CURDIR):/work'
		'-v=$(CURDIR)/.trivy-cache:/root/.cache/trivy'
		"$$image"
		image
		'--format=cyclonedx'
		'--output=/work/frontend-sbom-$(SBOM_VERSION).cdx.json'
		$(FRONTEND_IMAGE_NAME)
	)
	docker run "$${args[@]}"
