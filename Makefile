build:
	@docker compose build

collect-static:
	@CMD="poetry run python manage.py collectstatic --noinput" $(MAKE) exec-backend-command

django-shell:
	@CMD="poetry run python manage.py shell" $(MAKE) exec-backend-command-it

dump-data:
	@CMD="poetry run python manage.py dumpdata github owasp --indent=2" $(MAKE) exec-backend-command > data/nest.json

enrich-data: github_enrich_issues owasp-enrich-projects

exec-backend-command:
	@docker exec -i nest-backend $(CMD) 2>/dev/null

exec-backend-command-it:
	@docker exec -it nest-backend $(CMD) 2>/dev/null

github-update-owasp-organization:
	@echo "Updating OWASP GitHub organization"
	@CMD="poetry run python manage.py github_update_owasp_organization" $(MAKE) exec-backend-command

github-update-related-repositories:
	@echo "Updating related OWASP GitHub repositories"
	@CMD="poetry run python manage.py github_update_related_repositories" $(MAKE) exec-backend-command

github-enrich-issues:
	@CMD="poetry run python manage.py github_enrich_issues" $(MAKE) exec-backend-command

index-data:
	@echo "Indexing Nest data"
	@CMD="poetry run python manage.py algolia_reindex" $(MAKE) exec-backend-command

load-data:
	@CMD="poetry run python manage.py load_data" $(MAKE) exec-backend-command

merge-migrations:
	@CMD="poetry run python manage.py makemigrations --merge" $(MAKE) exec-backend-command

migrate:
	@CMD="poetry run python manage.py migrate" $(MAKE) exec-backend-command

migrations:
	@CMD="poetry run python manage.py makemigrations" $(MAKE) exec-backend-command

owasp-aggregate-projects:
	@echo "Aggregating OWASP projects"
	@CMD="poetry run python manage.py owasp_aggregate_projects" $(MAKE) exec-backend-command

owasp-enrich-projects:
	@CMD="poetry run python manage.py owasp_enrich_projects" $(MAKE) exec-backend-command

owasp-scrape-owasp-org:
	@echo "Scraping OWASP site projects data"
	@CMD="poetry run python manage.py owasp_scrape_owasp_org" $(MAKE) exec-backend-command

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
	@CMD="/bin/bash" $(MAKE) exec-backend-command-it

sync-data: \
	github-update-owasp-organization \
	owasp-scrape-owasp-org \
	github-update-related-repositories \
	owasp-aggregate-projects

test:
	@docker build -f backend/Dockerfile.test backend -t nest-backend-test
	@docker run -e DJANGO_CONFIGURATION=Test nest-backend-test poetry run pytest

update-data: sync-data enrich-data index-data
