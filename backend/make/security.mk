.PHONY: backend-dependency-audit backend-security-image-scan

backend-dependency-audit:
	@echo "Auditing backend Python dependencies..."
	@$(MAKE) run-cmd CMD='cd backend && \
		poetry export -f requirements.txt --all-groups -o /tmp/backend-requirements.txt && \
		pip-audit --disable-pip -r /tmp/backend-requirements.txt'

backend-security-image-scan:
	@if [ "$(BACKEND_IMAGE_NAME)" = "nest-backend-local" ]; then \
		$(MAKE) backend-image-build; \
	fi
	@echo "Scanning image: $(BACKEND_IMAGE_NAME)..."
	@docker run \
		--rm \
		-v $(CURDIR)/.trivyignore.yaml:/.trivyignore.yaml:ro \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/.trivy.yaml:/.trivy.yaml:ro \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //; s/ AS .*//' | head -1) \
		image --config /.trivy.yaml \
		--image-config-scanners misconfig,secret \
		$(BACKEND_IMAGE_NAME)
