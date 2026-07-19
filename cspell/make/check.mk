.PHONY: cspell-check

CSPELL_CMD := cspell --config cspell/cspell.json --no-progress -r .

cspell-check:
ifeq ($(CI),true)
	@PATH="$(CURDIR)/cspell/node_modules/.bin:$(PATH)" $(CSPELL_CMD)
else
	@$(MAKE) code-checks CMD='$(CSPELL_CMD)'
endif
