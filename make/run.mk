.PHONY: run run-o11y

run: ## Run Nest application
	@export DOCKER_BUILDKIT=1
	compose_args=(
		'-f=docker-compose/local/compose.yaml'
		'-f=docker-compose/local/compose.override.yaml'
		'--project-name=nest-local'
	)
	docker compose "$${compose_args[@]}" build --quiet
	docker compose "$${compose_args[@]}" up --remove-orphans

run-o11y: ## Run Nest application with the observability stack
	@export DOCKER_BUILDKIT=1
	compose_args=(
		'-f=docker-compose/local/compose.yaml'
		'-f=docker-compose/local/compose.override.yaml'
		'-f=docker-compose/local/compose.o11y.yaml'
		'--project-name=nest-local'
	)
	docker compose "$${compose_args[@]}" build --quiet
	docker compose "$${compose_args[@]}" up --remove-orphans
