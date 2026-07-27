##@ Maintenance

.PHONY: clean compile-requirements graphql-codegen prune clean-dependencies clean-docker \
	clean-trivy-cache dependency-compile-requirements tooling-clean-dependencies

clean: ## Remove all generated files and containers
	@$(MAKE) clean-dependencies
	@$(MAKE) clean-docker
	@$(MAKE) clean-trivy-cache

compile-requirements: ## Regenerate hashed pip requirements
	@$(MAKE) dependency-compile-requirements

graphql-codegen: ## Regenerate GraphQL types
	@CMD="pnpm run graphql-codegen" $(MAKE) frontend-exec-command

prune: ## Prune Docker resources
	@docker builder prune --filter 'until=72h' -a -f
	@docker image prune --filter 'until=72h' -a -f
	@docker volume prune -f

# Implementation targets.

clean-dependencies:
	@$(MAKE) backend-clean-dependencies
	@$(MAKE) frontend-clean-dependencies
	@$(MAKE) tooling-clean-dependencies

clean-docker:
	@$(MAKE) backend-clean-docker
	@$(MAKE) docs-clean-docker
	@$(MAKE) frontend-clean-docker
	@$(MAKE) infrastructure-clean-docker

clean-trivy-cache:
	@rm -rf $(CURDIR)/.trivy-cache

dependency-compile-requirements:
	@docker run \
		--rm \
		--user $$(id -u):$$(id -g) \
		-e HOME=/tmp \
		-e PIP_ROOT_USER_ACTION=ignore \
		-v "$(CURDIR):/work" \
		-w /work \
		$$(grep -E '^FROM python:' docker/backend/Dockerfile.local | sed 's/^FROM //; s/ AS .*//' | head -1) \
		sh -c 'python -m pip install --no-warn-script-location --quiet pip-tools && \
		python -m piptools compile --no-strip-extras --generate-hashes \
		--output-file=.github/requirements/scripts.txt \
		.github/requirements/scripts.in && \
		python -m piptools compile --no-strip-extras --generate-hashes \
		--output-file=backend/requirements/build.txt \
		backend/requirements/build.in && \
		python -m piptools compile --no-strip-extras --generate-hashes \
		--output-file=backend/requirements/cluster-fuzz-lite.txt \
		backend/requirements/cluster-fuzz-lite.in && \
		python -m piptools compile --no-strip-extras --generate-hashes \
		--output-file=tools/requirements/pre-commit.txt \
		tools/requirements/pre-commit.in && \
		python -m piptools compile --no-strip-extras --generate-hashes \
		--output-file=tools/requirements/test.txt \
		tools/requirements/test.in'

tooling-clean-dependencies:
	@rm -rf node_modules
