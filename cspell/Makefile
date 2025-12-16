check-spelling: cspell-check

cspell-install:
	@DOCKER_BUILDKIT=1 docker build \
		--cache-from cspell \
		cspell \
		-t cspell

cspell-check: CMD="--no-progress -r /nest"
cspell-check: cspell-install cspell-run

cspell-run:
	@docker run \
		--user $(shell id -u):$(shell id -g) \
		--mount type=bind,src="$(PWD)",dst=/nest \
		--rm \
		cspell -c cspell/cspell.json "$(CMD)"

update-cspell-dependencies: cspell-install
	@-docker run \
		-it \
		--mount type=bind,src="$(PWD)",dst=/nest \
		--entrypoint=/bin/sh \
		--workdir=/nest/cspell \
		--rm \
		cspell -c "pnpm install && pnpm upgrade && rm -rf ./node_modules"
