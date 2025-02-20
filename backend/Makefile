exec-backend-command:
	@docker exec -i nest-backend $(CMD)

exec-backend-command-it:
	@docker exec -it nest-backend $(CMD) 2>/dev/null

exec-db-command:
	@docker exec -it nest-db $(CMD)

collect-static:
	@CMD="poetry run python manage.py collectstatic --noinput" $(MAKE) exec-backend-command

django-shell:
	@CMD="poetry run python manage.py shell" $(MAKE) exec-backend-command-it

dump-data:
	@echo "Dumping Nest data"
	@CMD="poetry run python manage.py dumpdata github owasp --indent=2" $(MAKE) exec-backend-command > backend/data/nest.json
	@gzip backend/data/nest.json

enrich-data: github-enrich-issues owasp-enrich-chapters owasp-enrich-committees owasp-enrich-projects

generate-sitemap:
	@CMD="poetry run python manage.py generate_sitemap" $(MAKE) exec-backend-command

github-enrich-issues:
	@echo "Enriching GitHub issues"
	@CMD="poetry run python manage.py github_enrich_issues" $(MAKE) exec-backend-command

github-update-owasp-organization:
	@echo "Updating OWASP GitHub organization"
	@CMD="poetry run python manage.py github_update_owasp_organization" $(MAKE) exec-backend-command

github-update-project-related-repositories:
	@echo "Updating OWASP project related GitHub repositories"
	@CMD="poetry run python manage.py github_update_project_related_repositories" $(MAKE) exec-backend-command

index-data:
	@echo "Indexing Nest data"
	@CMD="poetry run python manage.py algolia_reindex" $(MAKE) exec-backend-command
	@CMD="poetry run python manage.py algolia_update_replicas" $(MAKE) exec-backend-command
	@CMD="poetry run python manage.py algolia_update_synonyms" $(MAKE) exec-backend-command

load-data:
	@echo "Loading Nest data"
	@CMD="poetry run python manage.py load_data" $(MAKE) exec-backend-command
	@CMD="poetry run python manage.py load_sponsor_data" $(MAKE) exec-backend-command

merge-migrations:
	@CMD="poetry run python manage.py makemigrations --merge" $(MAKE) exec-backend-command

migrate:
	@CMD="poetry run python manage.py migrate" $(MAKE) exec-backend-command

migrations:
	@CMD="poetry run python manage.py makemigrations" $(MAKE) exec-backend-command

owasp-aggregate-projects:
	@echo "Aggregating OWASP projects"
	@CMD="poetry run python manage.py owasp_aggregate_projects" $(MAKE) exec-backend-command

owasp-enrich-chapters:
	@echo "Enriching OWASP chapters"
	@CMD="poetry run python manage.py owasp_enrich_chapters" $(MAKE) exec-backend-command

owasp-enrich-committees:
	@echo "Enriching OWASP committees"
	@CMD="poetry run python manage.py owasp_enrich_committees" $(MAKE) exec-backend-command

owasp-enrich-projects:
	@echo "Enriching OWASP projects"
	@CMD="poetry run python manage.py owasp_enrich_projects" $(MAKE) exec-backend-command

owasp-scrape-chapters:
	@echo "Scraping OWASP site chapters data"
	@CMD="poetry run python manage.py owasp_scrape_chapters" $(MAKE) exec-backend-command

owasp-scrape-committees:
	@echo "Scraping OWASP site committees data"
	@CMD="poetry run python manage.py owasp_scrape_committees" $(MAKE) exec-backend-command

owasp-scrape-projects:
	@echo "Scraping OWASP site projects data"
	@CMD="poetry run python manage.py owasp_scrape_projects" $(MAKE) exec-backend-command

poetry-update:
	@CMD="poetry update" $(MAKE) exec-backend-command

purge-data:
	@CMD="poetry run python manage.py purge_data" $(MAKE) exec-backend-command

recreate-schema:
	@CMD="psql -U nest_user_dev -d nest_db_dev -c \
		'DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO nest_user_dev'" \
	  	$(MAKE) exec-db-command 2>/dev/null
	$(MAKE) migrate

setup:
	@CMD="poetry run python manage.py createsuperuser" $(MAKE) exec-backend-command-it

shell-backend:
	@CMD="/bin/bash" $(MAKE) exec-backend-command-it

sync-data: update-data enrich-data index-data

test-backend:
	@docker build -f backend/Dockerfile.test backend -t nest-test-backend
	@docker run -e DJANGO_CONFIGURATION=Test nest-test-backend poetry run pytest

update-data: \
	github-update-owasp-organization \
	owasp-scrape-chapters \
	owasp-scrape-committees \
	owasp-scrape-projects \
	github-update-project-related-repositories \
	owasp-aggregate-projects
