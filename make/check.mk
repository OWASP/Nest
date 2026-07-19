##@ Checks

.PHONY: check check-fix code-checks-install code-checks cspell prettier prettier-fix eslint \
	eslint-fix pre-commit

CODE_CHECKS_MOUNT_ROOT := --mount type=volume,dst=/nest/node_modules
CODE_CHECKS_MOUNT_FRONTEND := --mount type=volume,dst=/nest/frontend/node_modules
CODE_CHECKS_MOUNT_CSPELL := --mount type=volume,dst=/nest/cspell/node_modules
CODE_CHECKS_MOUNT_PRECOMMIT := \
	--mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock \
	--mount type=volume,src=nest-code-checks-pre-commit,dst=/tmp/pre-commit \
	--mount type=volume,src=nest-code-checks-terraform-plugin-cache,dst=/tmp/terraform-plugin-cache \
	--mount type=volume,src=nest-code-checks-tflint,dst=/tmp/tflint/plugins

check: ## Run code quality checks
ifneq ($(CI),true)
	@$(MAKE) code-checks-install
endif
	@echo "================================== Pre-commit =================================="
	@$(MAKE) pre-commit CODE_CHECKS_SKIP_INSTALL=1
	@echo ""
	@echo "=================================== Prettier ==================================="
	@$(MAKE) prettier CODE_CHECKS_SKIP_INSTALL=1
	@echo ""
	@echo "==================================== ESLint ===================================="
	@$(MAKE) eslint CODE_CHECKS_SKIP_INSTALL=1
	@echo ""
	@echo "==================================== CSpell ===================================="
	@$(MAKE) cspell CODE_CHECKS_SKIP_INSTALL=1
	@echo ""

check-fix: ## Auto-fix Prettier and ESLint issues
ifneq ($(CI),true)
	@$(MAKE) code-checks-install
endif
	@$(MAKE) prettier-fix CODE_CHECKS_SKIP_INSTALL=1
	@$(MAKE) eslint-fix CODE_CHECKS_SKIP_INSTALL=1

code-checks-install:
	@DOCKER_BUILDKIT=1 docker build -q \
		--cache-from nest-code-checks \
		-f docker/code-checks/Dockerfile \
		-t nest-code-checks \
		. 1>/dev/null

code-checks:
ifeq ($(CI),true)
	@PATH="$(CURDIR)/node_modules/.bin:$(PATH)" $(CMD)
else
ifndef CODE_CHECKS_SKIP_INSTALL
	@$(MAKE) code-checks-install
endif
	@docker run --rm \
		--mount type=bind,src="$(CURDIR)",dst=/nest \
		$(CODE_CHECKS_MOUNTS) \
		--workdir=/nest \
		nest-code-checks \
		sh -c '$(CMD)'
endif

cspell: ## Run spell checker
	@$(MAKE) cspell-check

prettier: ## Verify Prettier formatting
	@$(MAKE) code-checks \
		CODE_CHECKS_MOUNTS='$(CODE_CHECKS_MOUNT_ROOT) $(CODE_CHECKS_MOUNT_FRONTEND)' \
		CMD='prettier --check --log-level warn .'
	@echo "Prettier: all matched files use Prettier code style."

prettier-fix: ## Auto-fix Prettier formatting
	@$(MAKE) code-checks \
		CODE_CHECKS_MOUNTS='$(CODE_CHECKS_MOUNT_ROOT) $(CODE_CHECKS_MOUNT_FRONTEND)' \
		CMD='prettier --log-level warn --write .'

eslint: ## Verify ESLint for e2e and frontend
	@$(MAKE) code-checks \
		CODE_CHECKS_MOUNTS='$(CODE_CHECKS_MOUNT_ROOT) $(CODE_CHECKS_MOUNT_FRONTEND)' \
		CMD='eslint --max-warnings=0 e2e frontend'
	@echo "ESLint: no issues found."

eslint-fix: ## Auto-fix ESLint issues
	@$(MAKE) code-checks \
		CODE_CHECKS_MOUNTS='$(CODE_CHECKS_MOUNT_ROOT) $(CODE_CHECKS_MOUNT_FRONTEND)' \
		CMD='eslint --fix --max-warnings=0 e2e frontend'

pre-commit: ## Run pre-commit hooks
	@$(MAKE) code-checks \
		CODE_CHECKS_MOUNTS='$(CODE_CHECKS_MOUNT_PRECOMMIT)' \
		CMD='pre-commit run --all-files --color=always --show-diff-on-failure'
