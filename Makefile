migrate:
	CMD="poetry run python manage.py migrate" $(MAKE) run-backend-command

build:
	docker compose build

run:
	docker compose up

pre-commit:
	pre-commit run -a

run-backend-command:
	docker compose run --rm backend $(CMD)

shell:
	CMD="/bin/bash" $(MAKE) run-backend-command
