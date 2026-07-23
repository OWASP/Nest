.PHONY: frontend-dependency-audit frontend-security-image-scan

frontend-dependency-audit:
	@echo "Auditing frontend npm dependencies..."
	@$(MAKE) run-cmd CMD='cd frontend && pnpm audit --audit-level=moderate'

frontend-security-image-scan:
	@if [ "$(FRONTEND_IMAGE_NAME)" = "nest-frontend-local" ]; then \
		$(MAKE) frontend-image-build; \
	fi
	@echo "Scanning image: $(FRONTEND_IMAGE_NAME)..."
	@docker run \
		--rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/.trivy.yaml:/.trivy.yaml:ro \
		-v $(CURDIR)/.trivyignore.yaml:/.trivyignore.yaml:ro \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		image --config /.trivy.yaml \
		--image-config-scanners misconfig,secret \
		$(FRONTEND_IMAGE_NAME)
