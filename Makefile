include backend/Makefile
include frontend/Makefile

build:
	@docker compose build

check: \
	pre-commit \
	format-frontend-code \
	lint-frontend-code

pre-commit:
	@pre-commit run -a

run:
	@docker compose build
	@docker compose up

test: \
	test-backend \
	test-frontend
