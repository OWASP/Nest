.PHONY: frontend-dependency-audit frontend-security-image-scan

frontend-dependency-audit:
	@echo "Auditing frontend npm dependencies..."
	@$(MAKE) code-checks CMD='cd frontend && pnpm audit --audit-level=moderate'

frontend-security-image-scan: frontend-image-build-local
	@echo "Scanning image: $(FRONTEND_IMAGE_NAME)..."
	image="$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //')"
	args=(
		'--rm'
		'-v=/var/run/docker.sock:/var/run/docker.sock'
		'-v=$(CURDIR)/.trivy.yaml:/.trivy.yaml:ro'
		'-v=$(CURDIR)/.trivyignore.yaml:/.trivyignore.yaml:ro'
		'-v=$(CURDIR)/.trivy-cache:/root/.cache/trivy'
		"$$image"
		image
		'--config=/.trivy.yaml'
		'--image-config-scanners=misconfig,secret'
		$(FRONTEND_IMAGE_NAME)
	)
	docker run "$${args[@]}"
