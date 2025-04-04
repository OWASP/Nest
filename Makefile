include backend/Makefile
include cspell/Makefile
include docs/Makefile
include frontend/Makefile
include schema/Makefile

build:
	@docker compose build

clean: \
	clean-backend \
	clean-frontend \
	clean-schema

check: \
	check-backend \
	check-frontend \
	check-spelling

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

run:
	@COMPOSE_BAKE=true docker compose -f docker/docker-compose-local.yaml up --build --remove-orphans

test: \
	test-nest-app \
	test-schema

test-nest-app: \
	test-backend \
	test-frontend

update-dependencies: \
	update-nest-app-dependencies \
	update-schema-dependencies

update-nest-app-dependencies: \
	update-backend-dependencies \
	update-cspell-dependencies \
	update-docs-dependencies \
	update-frontend-dependencies \
	update-pre-commit

update-pre-commit:
	@pre-commit autoupdate
