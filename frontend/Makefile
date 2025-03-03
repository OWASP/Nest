check-frontend: \
	format-frontend-code \
	lint-frontend-code

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
	test-frontend-e2e \
	test-frontend-unit

test-frontend-e2e:
	@docker build -f frontend/docker/Dockerfile.e2e.test frontend -t nest-test-frontend-e2e
	@docker run --env-file frontend/.env.example nest-test-frontend-e2e npm run test:e2e

test-frontend-unit:
	@docker build -f frontend/docker/Dockerfile.unit.test frontend -t nest-test-frontend-unit
	@docker run --env-file frontend/.env.example nest-test-frontend-unit npm run test:unit

update-frontend-dependencies:
	@CMD="pnpm update" $(MAKE) exec-frontend-command-it
