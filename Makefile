include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile

MAKEFLAGS += --no-print-directory

build:
	@docker compose build

clean: \
	clean-dependencies \
	clean-docker

clean-dependencies: \
	clean-backend-dependencies \
	clean-frontend-dependencies

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
	docker compose -f docker-compose/local.yaml --project-name nest-local build && \
	docker compose -f docker-compose/local.yaml --project-name nest-local up --remove-orphans

fuzz-test-backend:
	@COMPOSE_BAKE=true docker compose -f docker/docker-compose-fuzz.yaml up --build --abort-on-container-exit --remove-orphans

test: \
	test-nest-app

test-nest-app: \
	test-backend \
	test-frontend

update: \
	clean-dependencies \
	update-docs-dependencies \
	update-nest-app-dependencies \
	update-pre-commit

update-nest-app-dependencies: \
	update-backend-dependencies \
	update-cspell-dependencies \
	update-frontend-dependencies

update-pre-commit:
	@pre-commit autoupdate
