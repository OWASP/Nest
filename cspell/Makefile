check-spelling: cspell-check

cspell-install:
	@ # Check if cspell:ci image exists (from CI build step), tag it to 'cspell' if found,
	@ # otherwise build the image from scratch for local development.
	@docker image inspect cspell:ci >/dev/null 2>&1 && \
	@docker tag cspell:ci cspell || docker build -t cspell cspell

cspell-check: CMD="--no-progress -r /nest"
cspell-check: cspell-install cspell-run

cspell-run:
	@docker run \
		--mount type=bind,src="$(CURDIR)",dst=/nest \
		--rm \
		cspell -c cspell/cspell.json "$(CMD)"

update-cspell-dependencies: cspell-install
	@-docker run \
		--entrypoint=/bin/sh \
		--interactive \
		--mount type=bind,src="$(CURDIR)",dst=/nest \
		--rm \
		--tty \
		--workdir=/nest/cspell \
		cspell -c "pnpm install && pnpm upgrade && rm -rf ./node_modules"
