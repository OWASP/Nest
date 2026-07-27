.PHONY: run

LOCAL_COMPOSE_FILES = \
	-f docker-compose/local/compose.yaml \
	-f docker-compose/local/compose.override.yaml

run: ## Run Nest application
	@DOCKER_BUILDKIT=1 \
	docker compose $(LOCAL_COMPOSE_FILES) --project-name nest-local build && \
	docker compose $(LOCAL_COMPOSE_FILES) --project-name nest-local up --remove-orphans
