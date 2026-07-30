.PHONY: frontend-clean-dependencies frontend-clean-docker

frontend-clean-dependencies:
	@rm -rf frontend/.next
	@rm -rf frontend/.pnpm-store
	@rm -rf frontend/node_modules

frontend-clean-docker:
	@docker container rm -f nest-frontend >/dev/null 2>&1 || true
	@docker image rm -f nest-local-frontend >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_frontend-next >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_frontend-node-modules >/dev/null 2>&1 || true
