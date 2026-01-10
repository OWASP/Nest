check-spelling: cspell-check

cspell-install:
	@docker image inspect cspell:ci >/dev/null 2>&1 && \
	docker tag cspell:ci cspell || \
	docker build -t cspell cspell

cspell-check: CMD="--no-progress -r /nest"
cspell-check: cspell-install cspell-run

cspell-run:
	@docker run \
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
