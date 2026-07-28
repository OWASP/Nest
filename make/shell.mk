##@ Shells

.PHONY: shell-backend shell-db shell-django shell-frontend

shell-backend: ## Open a backend container shell
	@$(MAKE) backend-exec-shell

shell-db: ## Open a database container shell
	@$(MAKE) backend-exec-db-shell

shell-django: ## Open a Django shell
	@$(MAKE) backend-django-shell

shell-frontend: ## Open a frontend container shell
	@$(MAKE) frontend-exec-shell
