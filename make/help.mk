##@ Getting Started

.PHONY: help

HELP_MAKEFILES := make/help.mk make/run.mk make/check.mk make/test.mk \
	backend/make/test.mk backend/make/clusterfuzz.mk frontend/make/test.mk \
	e2e/make/test.mk infrastructure/Makefile \
	make/check-test.mk make/maintenance.mk backend/make/django.mk \
	backend/make/maintenance.mk backend/make/data.mk make/shell.mk make/security.mk

help: ## Display this help
	@[ -t 1 ] && c='\033[36m' r='\033[0m' b='\033[1m' || c='' r='' b=''; \
	awk -v c="$$c" -v r="$$r" -v b="$$b" ' \
	function flush_section(   n, i, j, keys, tmp) { \
		if (section == "") return; \
		printf "\n" b "%s" r "\n", section; \
		n = 0; \
		for (t in targets) keys[++n] = t; \
			for (i = 1; i <= n; i++) { \
				for (j = i + 1; j <= n; j++) { \
					if (keys[j] < keys[i]) { \
						tmp = keys[i]; keys[i] = keys[j]; keys[j] = tmp; \
						} \
			} \
		} \
		for (i = 1; i <= n; i++) { \
			printf "  " c "%-30s" r " %s\n", keys[i], targets[keys[i]]; \
			} \
		delete targets; \
	} \
	BEGIN { FS = ":.*##"; printf "\nUsage:\n  make " c "<target>" r "\n" } \
	/^##@/ { flush_section(); section = substr($$0, 5) } \
	/^[a-zA-Z0-9_-]+:.*?## / { targets[$$1] = $$2 } \
	END { flush_section() }' \
	$(HELP_MAKEFILES)
