build:
	@docker compose build

collect-static:
	@CMD="poetry run python manage.py collectstatic --noinput" $(MAKE) exec-backend-command

django-shell:
	@CMD="poetry run python manage.py shell" $(MAKE) exec-backend-command

dump-data:
	@CMD="poetry run python manage.py dumpdata github owasp --indent=2" $(MAKE) exec-backend-command > data/nest.json

exec-backend-command:
	@docker exec -it nest-backend $(CMD) 2>/dev/null

github-sync-owasp-organization:
	@CMD="poetry run python manage.py github_sync_owasp_organization" $(MAKE) exec-backend-command

github-sync-related-repositories:
	@CMD="poetry run python manage.py github_sync_related_repositories" $(MAKE) exec-backend-command

github-enrich-issues:
	@CMD="poetry run python manage.py github_enrich_issues" $(MAKE) exec-backend-command

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

owasp-aggregate-projects-data:
	@CMD="poetry run python manage.py owasp_aggregate_projects_data" $(MAKE) exec-backend-command

owasp-scrape-site-data:
	@CMD="poetry run python manage.py owasp_scrape_site_data" $(MAKE) exec-backend-command

pre-commit:
	@pre-commit run -a

purge-data:
	@CMD="poetry run python manage.py purge_data" $(MAKE) exec-backend-command

run:
	@docker compose build
	@docker compose up

setup:
	@CMD="poetry run python manage.py createsuperuser" $(MAKE) exec-backend-command

shell:
	@CMD="/bin/bash" $(MAKE) exec-backend-command

sync: \
	github-sync-owasp-organization \
	owasp-scrape-site-data \
	github-sync-related-repositories \
	github-enrich-issues \
	owasp-aggregate-projects-data

test:
	@docker build -f backend/Dockerfile.test backend -t nest-backend-test 2>/dev/null
	@docker run -e DJANGO_CONFIGURATION=Test nest-backend-test poetry run pytest

update: sync index
