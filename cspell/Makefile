.PHONY: audit-cspell-dependencies cspell cspell-check cspell-install cspell-run \
	update-cspell-dependencies

##@ CSpell

cspell: ## Run spell checker
cspell: cspell-check

cspell-install:
	@docker build -q \
		--cache-from cspell \
		-t cspell \
		-f docker/cspell/Dockerfile \
		cspell 1>/dev/null

cspell-check: CMD="--no-progress -r /nest"
cspell-check: cspell-install cspell-run

cspell-run:
	@docker run \
		--mount type=bind,src="$(CURDIR)",dst=/nest \
		--rm \
		cspell -c cspell/cspell.json "$(CMD)"

audit-cspell-dependencies: ## Audit cspell npm dependencies
	@echo "Auditing cspell npm dependencies..."
	@cd cspell && pnpm audit --audit-level=$(AUDIT_LEVEL)

update-cspell-dependencies: cspell-install
	@-docker run \
		--entrypoint=/bin/sh \
		--interactive \
		--mount type=bind,src="$(CURDIR)",dst=/nest \
		--rm \
		--tty \
		--workdir=/nest/cspell \
		cspell -c "pnpm install && pnpm upgrade && rm -rf ./node_modules"
