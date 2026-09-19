.PHONY: tools-renew-security-txt tools-renew-security-txt-image-build \
	tools-renew-security-txt-run

tools-renew-security-txt: ## Generate a Nest security PGP key and renew security.txt
	@$(MAKE) tools-renew-security-txt-run

# Implementation targets.

SECURITY_TXT_IMAGE = nest-security-txt

tools-renew-security-txt-image-build:
	@args=(
		'-q'
		'--cache-from=$(SECURITY_TXT_IMAGE)'
		'-f=docker/tools/Dockerfile.security'
		.
		'-t=$(SECURITY_TXT_IMAGE)'
	)
	DOCKER_BUILDKIT=1 docker build "$${args[@]}" 1>/dev/null

tools-renew-security-txt-run: tools-renew-security-txt-image-build
	@args=(
		'--rm'
		"--user=$$(id -u):$$(id -g)"
		'-e=HOME=/tmp'
		'-e=NEST_SECURITY_PGP_PASSPHRASE'
		"-v=$(CURDIR):/work"
		'-w=/work'
		$(SECURITY_TXT_IMAGE)
		$(RENEW_SECURITY_TXT_ARGS)
	)
	docker run "$${args[@]}"
