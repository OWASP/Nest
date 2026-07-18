##@ Data

.PHONY: dump-data enrich-data fetch-nest-dump index-data load-data load-data-e2e load-data-fuzz \
	load-data-staging purge-data purge-data-e2e purge-data-fuzz recreate-schema restore-backup \
	save-backup sync-data update-data upload-nest-dump backend-data-dump backend-data-enrich \
	backend-data-fetch-nest-dump backend-data-index backend-data-load backend-data-load-e2e \
	backend-data-load-fuzz backend-data-load-staging backend-data-purge backend-data-purge-e2e \
	backend-data-purge-fuzz backend-data-recreate-schema backend-data-restore-backup \
	backend-data-save-backup backend-data-sync backend-data-update backend-data-upload-nest-dump

dump-data:
	@$(MAKE) backend-data-dump

enrich-data:
	@$(MAKE) backend-data-enrich

fetch-nest-dump:
	@$(MAKE) backend-data-fetch-nest-dump

index-data: ## Index data for Algolia search
	@$(MAKE) backend-data-index

load-data: ## Load database dump data
	@$(MAKE) backend-data-load

load-data-e2e:
	@$(MAKE) backend-data-load-e2e

load-data-fuzz:
	@$(MAKE) backend-data-load-fuzz

load-data-staging:
	@$(MAKE) backend-data-load-staging

purge-data: ## Purge database data
	@$(MAKE) backend-data-purge

purge-data-e2e:
	@$(MAKE) backend-data-purge-e2e

purge-data-fuzz:
	@$(MAKE) backend-data-purge-fuzz

recreate-schema: ## Recreate the local database schema
	@$(MAKE) backend-data-recreate-schema

restore-backup: ## Restore the Nest data backup
	@$(MAKE) backend-data-restore-backup

save-backup: ## Save the Nest data backup
	@$(MAKE) backend-data-save-backup

sync-data:
	@$(MAKE) backend-data-sync

update-data:
	@$(MAKE) backend-data-update

upload-nest-dump:
	@$(MAKE) backend-data-upload-nest-dump

# Implementation targets.

backend-data-dump:
	@echo "Dumping Nest data"
	@CMD="python manage.py dump_data" $(MAKE) backend-exec-command-it

backend-data-enrich:
	@$(MAKE) github-enrich-issues
	@$(MAKE) owasp-enrich-chapters
	@$(MAKE) owasp-enrich-committees
	@$(MAKE) owasp-enrich-events
	@$(MAKE) owasp-enrich-projects

backend-data-fetch-nest-dump:
	@DOCKER_BUILDKIT=1 docker compose \
		-f docker-compose/e2e/compose.yaml \
		run \
		--no-deps \
		--rm \
		backend python -m scripts.fetch_nest_dump

backend-data-index:
	@echo "Indexing Nest data"
	@CMD="python manage.py algolia_reindex" $(MAKE) backend-exec-command
	@CMD="python manage.py algolia_update_replicas" $(MAKE) backend-exec-command
	@CMD="python manage.py algolia_update_synonyms" $(MAKE) backend-exec-command

backend-data-load: backend-data-fetch-nest-dump
	@echo "Loading Nest data"
	@CMD="pg_restore -U nest_user_dev -d nest_db_dev < ./backend/data/nest.dump" $(MAKE) backend-exec-db-command

backend-data-load-e2e: backend-data-fetch-nest-dump
	@echo "Loading Nest e2e data"
	@CMD="pg_restore -U nest_user_e2e -d nest_db_e2e < ./backend/data/nest.dump" $(MAKE) backend-exec-db-command-e2e

backend-data-load-fuzz: backend-data-fetch-nest-dump
	@echo "Loading Nest fuzz data"
	@CMD="pg_restore -U nest_user_fuzz -d nest_db_fuzz < ./backend/data/nest.dump" $(MAKE) backend-exec-db-command-fuzz

backend-data-load-staging: backend-data-fetch-nest-dump
	@echo "Loading Nest staging data"
	@CMD="pg_restore -U nest_user_staging -d nest_db_staging < ./backend/data/nest.dump" $(MAKE) backend-exec-db-command-fuzz

backend-data-purge:
	@CMD="python manage.py purge_data" $(MAKE) backend-exec-command

backend-data-purge-e2e:
	@CMD="python manage.py purge_data" $(MAKE) backend-exec-command-e2e

backend-data-purge-fuzz:
	@CMD="python manage.py purge_data" $(MAKE) backend-exec-command-fuzz

backend-data-recreate-schema:
	@echo "Recreating Nest schema"
	@CMD="psql -U nest_user_dev -d nest_db_dev -c \
		'DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO nest_user_dev'" \
		$(MAKE) backend-exec-db-command-it 2>/dev/null
	@$(MAKE) backend-django-migrate

backend-data-restore-backup:
	@echo "Restoring Nest backup"
	@CMD="python manage.py restore_backup" $(MAKE) backend-exec-command

backend-data-save-backup:
	@echo "Saving Nest backup"
	@CMD="sh -c 'set -o pipefail; \
		trap \"rm -f data/backup.json.gz.tmp\" EXIT; \
		python manage.py dumpdata \
		--natural-primary \
		--natural-foreign \
		--indent=2 | gzip > data/backup.json.gz.tmp && \
		mv data/backup.json.gz.tmp data/backup.json.gz'" \
		$(MAKE) backend-exec-command

backend-data-sync:
	@$(MAKE) backend-data-update
	@$(MAKE) backend-data-enrich
	@$(MAKE) backend-data-index

backend-data-update:
	@$(MAKE) github-update-owasp-organization
	@$(MAKE) owasp-scrape-chapters
	@$(MAKE) owasp-scrape-committees
	@$(MAKE) owasp-scrape-projects
	@$(MAKE) github-add-related-repositories
	@$(MAKE) github-update-related-organizations
	@$(MAKE) github-update-users
	@$(MAKE) owasp-aggregate-projects
	@$(MAKE) owasp-aggregate-entity-contributions
	@$(MAKE) owasp-aggregate-member-contributions
	@$(MAKE) owasp-update-events
	@$(MAKE) owasp-sync-posts
	@$(MAKE) owasp-update-sponsors
	@$(MAKE) slack-sync-data

backend-data-upload-nest-dump:
	@cd backend && poetry run python -m scripts.upload_nest_dump
