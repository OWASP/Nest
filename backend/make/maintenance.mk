.PHONY: compile-backend-requirements backend-clean-dependencies backend-clean-docker \
	backend-dependency-compile-requirements

compile-backend-requirements: ## Regenerate hashed backend requirements
	@$(MAKE) backend-dependency-compile-requirements

# Implementation targets.

backend-clean-dependencies:
	@rm -rf backend/.cache
	@rm -rf backend/.local
	@rm -rf backend/.pytest_cache
	@rm -rf backend/.ruff_cache
	@rm -rf backend/.venv

backend-clean-docker:
	@docker container rm -f nest-backend >/dev/null 2>&1 || true
	@docker container rm -f nest-cache >/dev/null 2>&1 || true
	@docker container rm -f nest-db >/dev/null 2>&1 || true
	@docker container rm -f nest-worker >/dev/null 2>&1 || true
	@docker image rm -f nest-local-backend >/dev/null 2>&1 || true
	@docker image rm -f nest-snapshot-video >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_backend-venv >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_cache-data >/dev/null 2>&1 || true

backend-dependency-compile-requirements:
	@docker run \
		--rm \
		--user $$(id -u):$$(id -g) \
		-e HOME=/tmp \
		-e PIP_ROOT_USER_ACTION=ignore \
		-v "$(CURDIR):/work" \
		-w /work \
		$$(grep -E '^FROM python:' docker/backend/Dockerfile.local | sed 's/^FROM //; s/ AS .*//' | head -1) \
		sh -c 'python -m pip install --no-warn-script-location --quiet pip-tools && \
		python -m piptools compile --no-strip-extras --generate-hashes --output-file=backend/requirements/build.txt backend/requirements/build.in && \
		python -m piptools compile --no-strip-extras --generate-hashes --output-file=backend/requirements/cluster-fuzz-lite.txt backend/requirements/cluster-fuzz-lite.in && \
		python -m piptools compile --no-strip-extras --generate-hashes --output-file=backend/requirements/pre-commit.txt backend/requirements/pre-commit.in'
