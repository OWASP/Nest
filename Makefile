include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile
include schema/Makefile

build:
	@docker compose build

clean: \
	clean-dependencies \
	clean-docker

clean-dependencies: \
	clean-backend-dependencies \
	clean-frontend-dependencies \
	clean-schema-dependencies

clean-docker: \
	clean-backend-docker \
	clean-docs-docker \
	clean-frontend-docker

check: \
	check-spelling \
	check-backend \
	check-frontend

check-backend: \
	pre-commit

check-test: \
	check \
	test

check-test-backend: \
	pre-commit \
	test-backend

check-test-frontend: \
	check-frontend \
	test-frontend

pre-commit:
	@pre-commit run -a

prune:
	@docker builder prune --filter 'until=72h' -a -f
	@docker image prune --filter 'until=72h' -a -f
	@docker volume prune -f

run:
	@COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
	docker compose -f docker/docker-compose-local.yaml build && \
	docker compose -f docker/docker-compose-local.yaml up --remove-orphans

test: \
	test-nest-app \
	test-schema

test-nest-app: \
	test-backend \
	test-frontend

update: \
	clean-dependencies \
	update-docs-dependencies \
	update-nest-app-dependencies \
	update-pre-commit \
	update-schema-dependencies

update-nest-app-dependencies: \
	update-backend-dependencies \
	update-cspell-dependencies \
	update-frontend-dependencies

update-pre-commit:
	@pre-commit autoupdate
