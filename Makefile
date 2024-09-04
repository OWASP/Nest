build:
	@docker compose build
	@CMD="poetry install" $(MAKE) run-backend-command
	@CMD="poetry run python manage.py migrate" $(MAKE) run-backend-command

collect-static:
	@CMD="poetry run python manage.py collectstatic --noinput" $(MAKE) run-backend-command

github-sync-owasp-organization:
	@CMD="poetry run python manage.py github_sync_owasp_organization" $(MAKE) run-backend-command

github-sync-related-repositories:
	@CMD="poetry run python manage.py github_sync_related_repositories" $(MAKE) run-backend-command

migrate:
	@CMD="poetry run python manage.py migrate" $(MAKE) run-backend-command

migrations:
	@CMD="poetry run python manage.py makemigrations" $(MAKE) run-backend-command

owasp-scrape-site-data:
	@CMD="poetry run python manage.py owasp_scrape_site_data" $(MAKE) run-backend-command

owasp-update-projects:
	@CMD="poetry run python manage.py owasp_update_projects" $(MAKE) run-backend-command

pre-commit:
	@pre-commit run -a

run:
	@docker compose up

run-backend-command:
	@docker compose run --rm backend $(CMD)

shell:
	@CMD="/bin/bash" $(MAKE) run-backend-command

sync:
	$(MAKE) github-sync-owasp-organization
	$(MAKE) owasp-scrape-site-data
	$(MAKE) github-sync-related-repositories
	$(MAKE) owasp-update-projects

test:
	@cd backend && poetry run pytest; cd ..
