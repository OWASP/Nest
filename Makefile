include backend/Makefile
include cspell/Makefile
include frontend/Makefile
include schema/Makefile

build:
	@docker compose build

check-all: \
	check-code-style \
	check-spelling

check-code-style: \
	pre-commit \
	check-code-style-frontend

check-test-all: \
	check-all \
	test-all

pre-commit:
	@pre-commit run -a

run:
	@docker compose build
	@docker compose up

test-all: \
	test-nest-app \
	test-schema \

test-nest-app: \
	test-backend \
	test-frontend
