##@ Checks

.PHONY: check check-fix code-checks-install code-checks cspell prettier prettier-fix eslint \
	eslint-fix pre-commit

check: ## Run code quality checks
	@echo "================================== Pre-commit =================================="
	@$(MAKE) pre-commit
	@echo ""
	@echo "=================================== Prettier ==================================="
	@$(MAKE) prettier
	@echo ""
	@echo "==================================== ESLint ===================================="
	@$(MAKE) eslint
	@echo ""
	@echo "==================================== CSpell ===================================="
	@$(MAKE) cspell
	@echo ""

check-fix: ## Auto-fix Prettier and ESLint issues
	@$(MAKE) prettier-fix
	@$(MAKE) eslint-fix

code-checks-install:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from nest-code-checks \
		-f docker/code-checks/Dockerfile \
		-t nest-code-checks \
		. 1>/dev/null

# Named node_modules volumes are keyed by lockfile hash so they seed once and refresh on lockfile change.
code-checks:
ifeq ($(CI),true)
	@PATH="$(CURDIR)/node_modules/.bin:$(PATH)" $(CMD)
else
	@$(MAKE) code-checks-install
	@docker run --rm -t \
		--mount type=bind,src="$(CURDIR)",dst=/nest \
		--mount type=volume,src=nest-code-checks-node-modules-$(shell shasum -a 256 pnpm-lock.yaml | cut -c1-12),dst=/nest/node_modules,readonly \
		--mount type=volume,src=nest-code-checks-frontend-node-modules-$(shell shasum -a 256 frontend/pnpm-lock.yaml | cut -c1-12),dst=/nest/frontend/node_modules,readonly \
		--mount type=volume,src=nest-code-checks-cspell-node-modules-$(shell shasum -a 256 cspell/pnpm-lock.yaml | cut -c1-12),dst=/nest/cspell/node_modules,readonly \
		--mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock \
		--mount type=volume,src=nest-code-checks-pre-commit,dst=/tmp/pre-commit \
		--mount type=volume,src=nest-code-checks-terraform-plugin-cache,dst=/tmp/terraform-plugin-cache \
		--mount type=volume,src=nest-code-checks-tflint,dst=/tmp/tflint/plugins \
		--workdir=/nest \
		nest-code-checks \
		sh -c '$(CMD)'
endif

cspell: ## Run spell checker
	@$(MAKE) cspell-check

prettier: ## Verify Prettier formatting
	@$(MAKE) code-checks CMD='prettier --check --log-level warn .'
	@echo "Prettier: all matched files use Prettier code style."

prettier-fix: ## Auto-fix Prettier formatting
	@$(MAKE) code-checks CMD='prettier --log-level warn --write .'

eslint: ## Verify ESLint for e2e and frontend
	@$(MAKE) code-checks CMD='eslint --max-warnings=0 e2e frontend'
	@echo "ESLint: no issues found."

eslint-fix: ## Auto-fix ESLint issues
	@$(MAKE) code-checks CMD='eslint --fix --max-warnings=0 e2e frontend'

pre-commit: ## Run pre-commit hooks
	@$(MAKE) code-checks CMD='pre-commit run --all-files --color=always --show-diff-on-failure'
