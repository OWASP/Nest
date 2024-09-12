build:
	@docker compose build

collect-static:
	@CMD="poetry run python manage.py collectstatic --noinput" $(MAKE) exec-backend-command

dump-data:
	@CMD="poetry run python manage.py dumpdata github owasp --indent=2 --output=data/nest.json" $(MAKE) exec-backend-command

exec-backend-command:
	@docker exec -it nest-backend $(CMD) 2>/dev/null

github-sync-owasp-organization:
	@CMD="poetry run python manage.py github_sync_owasp_organization" $(MAKE) exec-backend-command

github-sync-related-repositories:
	@CMD="poetry run python manage.py github_sync_related_repositories" $(MAKE) exec-backend-command

index:
	@CMD="poetry run python manage.py algolia_reindex" $(MAKE) exec-backend-command

load-data:
	@CMD="poetry run python manage.py load_data" $(MAKE) exec-backend-command

merge-migrations:
	@CMD="poetry run python manage.py makemigrations --merge" $(MAKE) exec-backend-command

migrate:
	@CMD="poetry run python manage.py migrate" $(MAKE) exec-backend-command

migrations:
	@CMD="poetry run python manage.py makemigrations" $(MAKE) exec-backend-command

owasp-scrape-site-data:
	@CMD="poetry run python manage.py owasp_scrape_site_data" $(MAKE) exec-backend-command

owasp-update-projects:
	@CMD="poetry run python manage.py owasp_update_projects" $(MAKE) exec-backend-command

pre-commit:
	@pre-commit run -a

purge-data:
	@CMD="poetry run python manage.py purge_data" $(MAKE) exec-backend-command

run:
	@$(MAKE) build
	@docker compose up

setup:
	@CMD="poetry run python manage.py createsuperuser" $(MAKE) exec-backend-command

shell:
	@CMD="/bin/bash" $(MAKE) exec-backend-command

sync:
	@$(MAKE) github-sync-owasp-organization
	@$(MAKE) owasp-scrape-site-data
	@$(MAKE) github-sync-related-repositories
	@$(MAKE) owasp-update-projects

test:
	@docker build -f backend/Dockerfile.test backend -t nest-backend-test 2>/dev/null
	@docker run -e DJANGO_CONFIGURATION=Test nest-backend-test poetry run pytest 2>/dev/null

update:
	@$(MAKE) sync
	@$(MAKE) index
