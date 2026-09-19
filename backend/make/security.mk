.PHONY: backend-dependency-audit backend-security-image-scan \
	backend-security-maybe-build-image

backend-dependency-audit:
	@echo "Auditing backend Python dependencies..."
	@$(MAKE) code-checks CMD='cd backend && \
		req=$$(mktemp) && trap "rm -f \"$$req\"" EXIT && \
		poetry export -f requirements.txt --all-groups -o "$$req" && \
		pip-audit --disable-pip -r "$$req"'

# Keep $(MAKE) out of the scan recipe so `make -n` does not run docker under .ONESHELL.
backend-security-maybe-build-image:
	@if [ "$(BACKEND_IMAGE_NAME)" = "nest-backend-local" ]; then
		$(MAKE) backend-image-build
	fi

backend-security-image-scan: backend-security-maybe-build-image
	@echo "Scanning image: $(BACKEND_IMAGE_NAME)..."
	image="$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //; s/ AS .*//' | head -1)"
	args=(
		'--rm'
		'-v=$(CURDIR)/.trivyignore.yaml:/.trivyignore.yaml:ro'
		'-v=/var/run/docker.sock:/var/run/docker.sock'
		'-v=$(CURDIR)/.trivy.yaml:/.trivy.yaml:ro'
		'-v=$(CURDIR)/.trivy-cache:/root/.cache/trivy'
		"$$image"
		image
		'--config=/.trivy.yaml'
		'--image-config-scanners=misconfig,secret'
		$(BACKEND_IMAGE_NAME)
	)
	docker run "$${args[@]}"
