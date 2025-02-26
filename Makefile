include backend/Makefile
include cspell/Makefile
include frontend/Makefile
include schema/Makefile

build:
	@docker compose build

check-all: \
	check-backend \
	check-frontend \
	check-spelling

check-backend: \
	pre-commit

check-test-all: \
	check-all \
	test-all

check-test-backend: \
	pre-commit \
	test-backend

check-test-frontend: \
	check-frontend \
	unittest-frontend \
	e2etest-frontend

pre-commit:
	@pre-commit run -a

run:
	@docker compose -f docker/docker-compose-local.yaml build
	@docker compose -f docker/docker-compose-local.yaml up --remove-orphans

test-all: \
	test-nest-app \
	test-schema

test-nest-app: \
	test-backend \
	unittest-frontend \
	e2etest-frontend

update-dependencies: \
	update-nest-app-dependencies \
	update-schema-dependencies

update-nest-app-dependencies: \
	update-backend-dependencies \
	update-frontend-dependencies
