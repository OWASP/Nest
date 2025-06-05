check-frontend: \
	format-frontend-code \
	lint-frontend-code

clean-frontend-dependencies:
	@rm -rf frontend/.next
	@rm -rf frontend/.pnpm-store
	@rm -rf frontend/node_modules

clean-frontend-docker:
	@docker container rm -f nest-frontend >/dev/null 2>&1 || true
	@docker image rm -f docker-frontend >/dev/null 2>&1 || true
	@docker volume rm -f docker_frontend-next >/dev/null 2>&1 || true
	@docker volume rm -f docker_frontend-node-modules >/dev/null 2>&1 || true

exec-frontend-command:
	@docker exec -t nest-frontend $(CMD)

exec-frontend-command-it:
	@docker exec -it nest-frontend $(CMD)

format-frontend-code:
	@CMD="pnpm run format" $(MAKE) exec-frontend-command

lint-frontend-code:
	@CMD="pnpm run lint" $(MAKE) exec-frontend-command

shell-frontend:
	@CMD="/bin/sh" $(MAKE) exec-frontend-command-it

test-frontend: \
	test-frontend-unit \
	test-frontend-e2e

test-frontend-e2e:
	@DOCKER_BUILDKIT=1 docker build \
		--cache-from nest-test-frontend-e2e \
		-f frontend/docker/Dockerfile.e2e.test frontend \
		-t nest-test-frontend-e2e
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-e2e pnpm run test:e2e

test-frontend-unit:
	@DOCKER_BUILDKIT=1 docker build \
		--cache-from nest-test-frontend-unit \
		-f frontend/docker/Dockerfile.unit.test frontend \
		-t nest-test-frontend-unit
	@docker run --env-file frontend/.env.example --rm nest-test-frontend-unit pnpm run test:unit

update-frontend-dependencies:
	@CMD="pnpm update" $(MAKE) exec-frontend-command-it
