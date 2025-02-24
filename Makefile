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
	test-frontend

pre-commit:
	@pre-commit run -a

run:
	@docker compose build
	@docker compose up

test-all: \
	test-nest-app \
	test-schema

test-nest-app: \
	test-backend \
	test-frontend

update-nest-app-dependencies: \
	update-backend-dependencies \
	update-frontend-dependencies
