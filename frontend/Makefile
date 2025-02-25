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

test-frontend:
	@docker build -f frontend/Dockerfile.test frontend -t nest-test-frontend
	@docker run --env-file frontend/.env.example nest-test-frontend npm run test

update-frontend-dependencies:
	@CMD="pnpm update" $(MAKE) exec-frontend-command-it
