include backend/Makefile
include cspell/Makefile
include frontend/Makefile
include schema/Makefile

build:
	@docker compose build

check: \
	pre-commit \
	check-frontend \
	spellcheck

pre-commit:
	@pre-commit run -a

run:
	@docker compose build
	@docker compose up

test: \
	test-backend \
	test-frontend

test-all: \
	test-backend \
	test-frontend \
	test-schema \
	pre-commit \
	check-frontend \
	spellcheck
