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

unittest-frontend:
	@docker build -f frontend/Dockerfile.unittesting frontend -t nest-unittesting-frontend
	@docker run --env-file frontend/.env.example nest-unittesting-frontend npm run test:jest

e2etest-frontend:
	@docker build -f frontend/Dockerfile.e2etesting frontend -t nest-e2etesting-frontend
	@docker run --env-file frontend/.env.example nest-e2etesting-frontend npm run test:playwright

update-frontend-dependencies:
	@CMD="npm update" $(MAKE) exec-frontend-command-it
