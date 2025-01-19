cspell-install:
	@docker build cspell -t cspell

cspell-check: CMD="--no-progress -r /nest"
cspell-check: cspell-install cspell-run

cspell-run:
	@-docker run \
		--mount type=bind,src="$(PWD)",dst=/nest \
		--rm \
		cspell -c cspell/cspell.json "$(CMD)"

cspell-update-deps: cspell-install
	@-docker run \
		--mount type=bind,src="$(PWD)",dst=/nest \
		--entrypoint=/bin/sh \
		--workdir=/nest/cspell \
		--rm \
		cspell -c "npm install && npm upgrade && rm -rf ./node_modules"

spellcheck: cspell-check
