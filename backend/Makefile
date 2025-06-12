clean-backend-dependencies:
	@rm -rf backend/.cache
	@rm -rf backend/.local
	@rm -rf backend/.venv

clean-backend-docker:
	@docker container rm -f nest-backend >/dev/null 2>&1 || true
	@docker image rm -f docker-backend >/dev/null 2>&1 || true
	@docker volume rm -f docker_backend-venv >/dev/null 2>&1 || true

exec-backend-command:
	@docker exec -i nest-backend $(CMD)

exec-backend-command-it:
	@docker exec -it nest-backend $(CMD) 2>/dev/null

exec-db-command-it:
	@docker exec -it nest-db $(CMD)

clear-cache:
	@CMD="python manage.py clear_cache" $(MAKE) exec-backend-command

collect-static:
	@CMD="python manage.py collectstatic --noinput" $(MAKE) exec-backend-command

django-shell:
	@CMD="python manage.py shell" $(MAKE) exec-backend-command-it

dump-data:
	@echo "Dumping Nest data"
	@CMD="python manage.py dumpdata github owasp --indent=2" $(MAKE) exec-backend-command > backend/data/nest.json
	@gzip backend/data/nest.json

enrich-data: \
	github-enrich-issues \
	owasp-enrich-chapters \
	owasp-enrich-committees \
	owasp-enrich-events \
	owasp-enrich-projects

generate-sitemap:
	@CMD="python manage.py generate_sitemap" $(MAKE) exec-backend-command

github-enrich-issues:
	@echo "Enriching GitHub issues"
	@CMD="python manage.py github_enrich_issues" $(MAKE) exec-backend-command

github-match-users:
	@CMD="python manage.py github_match_users $(MATCH_MODEL)" $(MAKE) exec-backend-command

github-update-owasp-organization:
	@echo "Updating OWASP GitHub organization"
	@CMD="python manage.py github_update_owasp_organization" $(MAKE) exec-backend-command

github-update-project-related-repositories:
	@echo "Updating OWASP project related GitHub repositories"
	@CMD="python manage.py github_update_project_related_repositories" $(MAKE) exec-backend-command

github-update-users:
	@echo "Updating GitHub users"
	@CMD="python manage.py github_update_users" $(MAKE) exec-backend-command

index-data:
	@echo "Indexing Nest data"
	@CMD="python manage.py algolia_reindex" $(MAKE) exec-backend-command
	@CMD="python manage.py algolia_update_replicas" $(MAKE) exec-backend-command
	@CMD="python manage.py algolia_update_synonyms" $(MAKE) exec-backend-command

load-data:
	@echo "Loading Nest data"
	@CMD="python manage.py load_data" $(MAKE) exec-backend-command

merge-migrations:
	@CMD="python manage.py makemigrations --merge" $(MAKE) exec-backend-command

migrate:
	@CMD="python manage.py migrate" $(MAKE) exec-backend-command

migrations:
	@CMD="python manage.py makemigrations" $(MAKE) exec-backend-command

owasp-aggregate-projects:
	@echo "Aggregating OWASP projects"
	@CMD="python manage.py owasp_aggregate_projects" $(MAKE) exec-backend-command

owasp-enrich-chapters:
	@echo "Enriching OWASP chapters"
	@CMD="python manage.py owasp_enrich_chapters" $(MAKE) exec-backend-command

owasp-enrich-committees:
	@echo "Enriching OWASP committees"
	@CMD="python manage.py owasp_enrich_committees" $(MAKE) exec-backend-command

owasp-enrich-events:
	@echo "Enriching OWASP events"
	@CMD="python manage.py owasp_enrich_events" $(MAKE) exec-backend-command

owasp-enrich-projects:
	@echo "Enriching OWASP projects"
	@CMD="python manage.py owasp_enrich_projects" $(MAKE) exec-backend-command

owasp-process-snapshots:
	@echo "Processing OWASP snapshots"
	@CMD="python manage.py owasp_process_snapshots" $(MAKE) exec-backend-command

owasp-update-project-health-metrics:
	@echo "Updating OWASP project health metrics"
	@CMD="python manage.py owasp_update_project_health_metrics" $(MAKE) exec-backend-command

owasp-update-project-health-metrics-scores:
	@echo "Updating OWASP project health metrics score"
	@CMD="python manage.py owasp_update_project_health_metrics_scores" $(MAKE) exec-backend-command

owasp-update-project-health-requirements:
	@echo "Updating OWASP project health requirements"
	@CMD="python manage.py owasp_update_project_health_requirements" $(MAKE) exec-backend-command

owasp-scrape-chapters:
	@echo "Scraping OWASP site chapters data"
	@CMD="python manage.py owasp_scrape_chapters" $(MAKE) exec-backend-command

owasp-scrape-committees:
	@echo "Scraping OWASP site committees data"
	@CMD="python manage.py owasp_scrape_committees" $(MAKE) exec-backend-command

owasp-scrape-projects:
	@echo "Scraping OWASP site projects data"
	@CMD="python manage.py owasp_scrape_projects" $(MAKE) exec-backend-command

owasp-sync-posts:
	@CMD="python manage.py owasp_sync_posts" $(MAKE) exec-backend-command

owasp-update-events:
	@echo "Getting OWASP events data"
	@CMD="python manage.py owasp_update_events" $(MAKE) exec-backend-command

owasp-update-sponsors:
	@echo "Getting OWASP sponsors data"
	@CMD="python manage.py owasp_update_sponsors" $(MAKE) exec-backend-command

purge-data:
	@CMD="python manage.py purge_data" $(MAKE) exec-backend-command

recreate-schema:
	@CMD="psql -U nest_user_dev -d nest_db_dev -c \
		'DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO nest_user_dev'" \
	  	$(MAKE) exec-db-command-it 2>/dev/null
	$(MAKE) migrate

setup:
	@CMD="python manage.py createsuperuser" $(MAKE) exec-backend-command-it

shell-backend:
	@CMD="/bin/sh" $(MAKE) exec-backend-command-it

shell-db:
	@CMD="/bin/sh" $(MAKE) exec-db-command-it

slack-sync-data:
	@echo "Syncing Slack data"
	@CMD="python manage.py slack_sync_data" $(MAKE) exec-backend-command

slack-sync-messages:
	@echo "Syncing Slack messages"
	@CMD="python manage.py slack_sync_messages" $(MAKE) exec-backend-command

sync-data: \
	update-data \
	enrich-data \
	index-data

test-backend:
	@DOCKER_BUILDKIT=1 docker build \
		--cache-from nest-test-backend \
		-f backend/docker/Dockerfile.test backend \
		-t nest-test-backend
	@docker run -e DJANGO_CONFIGURATION=Test --rm nest-test-backend pytest

update-backend-dependencies:
	@cd backend && poetry update

update-data: \
	github-update-owasp-organization \
	owasp-scrape-chapters \
	owasp-scrape-committees \
	owasp-scrape-projects \
	github-update-project-related-repositories \
	github-update-users \
	owasp-aggregate-projects \
	owasp-update-events \
	owasp-sync-posts \
	owasp-update-sponsors \
	slack-sync-data
