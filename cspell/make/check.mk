.PHONY: cspell-check

CSPELL_CMD := cspell --config cspell/cspell.json --no-progress -r .

cspell-check:
ifeq ($(CI),true)
	@PATH="$(CURDIR)/cspell/node_modules/.bin:$(PATH)" $(CSPELL_CMD)
else
	@$(MAKE) code-checks \
		CODE_CHECKS_MOUNTS='$(CODE_CHECKS_MOUNT_CSPELL)' \
		CMD='$(CSPELL_CMD)'
endif
