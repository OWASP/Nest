exec-frontend-command:
	@docker exec -i nest-frontend $(CMD)

format-frontend-code:
	@CMD="npm run format" $(MAKE) exec-frontend-command

lint-frontend-code:
	@CMD="npm run lint" $(MAKE) exec-frontend-command

test-frontend:
	@cd frontend && npm run test
