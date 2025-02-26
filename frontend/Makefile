check-frontend: \
	format-frontend-code \
	lint-frontend-code

exec-frontend-command:
	@docker exec -t nest-frontend $(CMD)

exec-frontend-command-it:
	@docker exec -it nest-frontend $(CMD)

format-frontend-code:
	@CMD="npm run format" $(MAKE) exec-frontend-command

lint-frontend-code:
	@CMD="npm run lint" $(MAKE) exec-frontend-command

shell-frontend:
	@CMD="/bin/sh" $(MAKE) exec-frontend-command-it

test-e2e-frontend:
	@docker build -f frontend/Dockerfile.e2e.test frontend -t nest-e2e-test-frontend
	@docker run --env-file frontend/.env.example nest-e2etesting-frontend npm run test:e2e

test-frontend: \
	test-unit-frontend \
	test-e2e-frontend

test-unit-frontend:
	@docker build -f frontend/docker/Dockerfile.unit.test frontend -t nest-unit-test-frontend
	@docker run --env-file frontend/.env.example nest-test-frontend npm run test:unit

update-frontend-dependencies:
	@CMD="npm update" $(MAKE) exec-frontend-command-it
