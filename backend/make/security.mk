.PHONY: backend-dependency-audit backend-security-image-scan

IMAGE_SCANNERS ?= misconfig,secret,vuln

backend-dependency-audit:
	@echo "Auditing backend Python dependencies..."
	@docker run \
		--rm \
		--user $$(id -u):$$(id -g) \
		-e HOME=/tmp \
		-e PIP_ROOT_USER_ACTION=ignore \
		-v "$(CURDIR):/work" \
		-w /work/backend \
		$$(grep -E '^FROM python:' docker/backend/Dockerfile.local | sed 's/^FROM //; s/ AS .*//' | head -1) \
		sh -c 'python -m pip install --no-warn-script-location --quiet poetry poetry-plugin-export pip-audit && \
		export PATH="$$HOME/.local/bin:$$PATH" && \
		poetry export -f requirements.txt --without-hashes --all-groups | \
		pip-audit -r /dev/stdin'

backend-security-image-scan:
	@if [ "$(BACKEND_IMAGE_NAME)" = "nest-backend-local" ]; then \
		$(MAKE) backend-image-build; \
	fi
	@echo "Scanning image: $(BACKEND_IMAGE_NAME)..."
	@docker run \
		--rm \
		-e TRIVY_SCANNERS="$(IMAGE_SCANNERS)" \
		-v $(CURDIR)/.trivyignore.yaml:/.trivyignore.yaml:ro \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/.trivy.yaml:/.trivy.yaml:ro \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		image --config /.trivy.yaml $(BACKEND_IMAGE_NAME)
