.PHONY: infrastructure-dependency-audit

infrastructure-dependency-audit:
	@echo "Auditing infrastructure Python dependencies..."
	@docker run \
		--rm \
		--user $$(id -u):$$(id -g) \
		-e HOME=/tmp \
		-e PIP_ROOT_USER_ACTION=ignore \
		-v "$(CURDIR):/work" \
		-w /work/infrastructure \
		$$(grep -E '^FROM python:' docker/infrastructure/Dockerfile.tests | sed 's/^FROM //; s/ AS .*//' | head -1) \
		sh -c 'python -m pip install --no-warn-script-location --quiet poetry poetry-plugin-export pip-audit && \
		export PATH="$$HOME/.local/bin:$$PATH" && \
		poetry export -f requirements.txt --without-hashes --with test -o /tmp/requirements.txt && \
		pip-audit -r /tmp/requirements.txt'
