.PHONY: docs-dependency-audit

docs-dependency-audit:
	@echo "Auditing docs Python dependencies..."
	@docker run \
		--rm \
		--user $$(id -u):$$(id -g) \
		-e HOME=/tmp \
		-e PIP_ROOT_USER_ACTION=ignore \
		-v "$(CURDIR):/work" \
		-w /work/docs \
		$$(grep -E '^FROM python:' docker/docs/Dockerfile.local | sed 's/^FROM //; s/ AS .*//' | head -1) \
		sh -c 'python -m pip install --no-warn-script-location --quiet poetry poetry-plugin-export pip-audit && \
		export PATH="$$HOME/.local/bin:$$PATH" && \
		poetry export -f requirements.txt --without-hashes --only main -o /tmp/requirements.txt && \
		pip-audit -r /tmp/requirements.txt'
