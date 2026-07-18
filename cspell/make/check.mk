.PHONY: cspell-check

cspell-check:
	@$(MAKE) code-checks CMD='cspell --config cspell/cspell.json --no-progress -r /nest'
