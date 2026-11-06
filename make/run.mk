.PHONY: run

run: ## Run Nest application
	@export DOCKER_BUILDKIT=1
	compose_args=(
		'-f=docker-compose/local/compose.yaml'
		'-f=docker-compose/local/compose.override.yaml'
		'--project-name=nest-local'
	)
	docker compose "$${compose_args[@]}" build --quiet
	docker compose "$${compose_args[@]}" up --remove-orphans
