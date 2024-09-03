build:
	@docker compose build
	@CMD="poetry install" $(MAKE) run-backend-local-command
	@CMD="poetry run python manage.py migrate" $(MAKE) run-backend-local-command

collect-static:
	@CMD="poetry run python manage.py collectstatic --noinput" $(MAKE) run-backend-local-command

migrate:
	@CMD="poetry run python manage.py migrate" $(MAKE) run-backend-local-command

migrations:
	@CMD="poetry run python manage.py makemigrations" $(MAKE) run-backend-local-command

run:
	@docker compose up

pre-commit:
	@pre-commit run -a

run-backend-local-command:
	@docker compose run --rm backend-local $(CMD)

shell:
	@CMD="/bin/bash" $(MAKE) run-backend-local-command

test:
	@cd backend && poetry run pytest; cd ..

github-sync-owasp-organization:
	@CMD="poetry run python manage.py github_sync_owasp_organization" $(MAKE) run-backend-local-command

github-sync-related-repositories:
	@CMD="poetry run python manage.py github_sync_related_repositories" $(MAKE) run-backend-local-command

owasp-scrape-site-data:
	@CMD="poetry run python manage.py owasp_scrape_site_data" $(MAKE) run-backend-local-command

owasp-update-projects:
	@CMD="poetry run python manage.py owasp_update_projects" $(MAKE) run-backend-local-command
