.PHONY: run run-o11y

LOCAL_COMPOSE_FILES = \
	-f docker-compose/local/compose.yaml \
	-f docker-compose/local/compose.override.yaml

O11Y_COMPOSE_FILES = \
	$(LOCAL_COMPOSE_FILES) \
	-f docker-compose/local/compose.o11y.yaml

run: ## Run Nest application
	@DOCKER_BUILDKIT=1 \
	docker compose $(LOCAL_COMPOSE_FILES) --project-name nest-local build && \
	docker compose $(LOCAL_COMPOSE_FILES) --project-name nest-local up --remove-orphans

run-o11y: ## Run Nest application with the observability stack
	@DOCKER_BUILDKIT=1 \
	docker compose $(O11Y_COMPOSE_FILES) --project-name nest-local build && \
	docker compose $(O11Y_COMPOSE_FILES) --project-name nest-local up --remove-orphans
