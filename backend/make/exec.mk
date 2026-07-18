.PHONY: exec-backend-command exec-backend-command-e2e exec-backend-command-e2e-it \
	exec-backend-command-fuzz exec-backend-command-fuzz-it exec-backend-command-it exec-db-command \
	exec-db-command-e2e exec-db-command-e2e-it exec-db-command-fuzz exec-db-command-fuzz-it \
	exec-db-command-it backend-exec-command backend-exec-command-e2e \
	backend-exec-command-e2e-it backend-exec-command-fuzz backend-exec-command-fuzz-it \
	backend-exec-command-it backend-exec-db-command backend-exec-db-command-e2e \
	backend-exec-db-command-e2e-it backend-exec-db-command-fuzz backend-exec-db-command-fuzz-it \
	backend-exec-db-command-it backend-exec-db-shell backend-exec-shell

exec-backend-command: ## Run a command in the backend container
	@$(MAKE) backend-exec-command

exec-backend-command-e2e: ## Run a command in the end-to-end backend container
	@$(MAKE) backend-exec-command-e2e

exec-backend-command-e2e-it: ## Run an interactive command in the end-to-end backend container
	@$(MAKE) backend-exec-command-e2e-it

exec-backend-command-fuzz: ## Run a command in the fuzz backend container
	@$(MAKE) backend-exec-command-fuzz

exec-backend-command-fuzz-it: ## Run an interactive command in the fuzz backend container
	@$(MAKE) backend-exec-command-fuzz-it

exec-backend-command-it: ## Run an interactive command in the backend container
	@$(MAKE) backend-exec-command-it

exec-db-command: ## Run a command in the database container
	@$(MAKE) backend-exec-db-command

exec-db-command-e2e: ## Run a command in the end-to-end database container
	@$(MAKE) backend-exec-db-command-e2e

exec-db-command-e2e-it: ## Run an interactive command in the end-to-end database container
	@$(MAKE) backend-exec-db-command-e2e-it

exec-db-command-fuzz: ## Run a command in the fuzz database container
	@$(MAKE) backend-exec-db-command-fuzz

exec-db-command-fuzz-it: ## Run an interactive command in the fuzz database container
	@$(MAKE) backend-exec-db-command-fuzz-it

exec-db-command-it: ## Run an interactive command in the database container
	@$(MAKE) backend-exec-db-command-it

# Implementation targets.

backend-exec-command:
ifeq ($(EXEC_MODE),direct)
	@$(CMD)
else
	@docker exec -i nest-backend $(CMD)
endif

backend-exec-command-e2e:
	@docker exec -i e2e-nest-backend $(CMD)

backend-exec-command-e2e-it:
	@docker exec -it e2e-nest-backend $(CMD)

backend-exec-command-fuzz:
	@docker exec -i fuzz-nest-backend $(CMD)

backend-exec-command-fuzz-it:
	@docker exec -it fuzz-nest-backend $(CMD)

backend-exec-command-it:
ifeq ($(EXEC_MODE),direct)
	@$(CMD)
else
	@docker exec -it nest-backend $(CMD) 2>/dev/null
endif

backend-exec-db-command:
	@docker exec -i nest-db $(CMD)

backend-exec-db-command-e2e:
	@docker exec -i e2e-nest-db $(CMD)

backend-exec-db-command-e2e-it:
	@docker exec -it e2e-nest-db $(CMD)

backend-exec-db-command-fuzz:
	@docker exec -i fuzz-nest-db $(CMD)

backend-exec-db-command-fuzz-it:
	@docker exec -it fuzz-nest-db $(CMD)

backend-exec-db-command-it:
	@docker exec -it nest-db $(CMD)

backend-exec-db-shell:
	@CMD="/bin/sh" $(MAKE) backend-exec-db-command-it

backend-exec-shell:
	@CMD="/bin/sh" $(MAKE) backend-exec-command-it
