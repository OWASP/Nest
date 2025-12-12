include backend/apps/ai/Makefile
include backend/apps/github/Makefile
include backend/apps/mentorship/Makefile
include backend/apps/nest/Makefile
include backend/apps/owasp/Makefile
include backend/apps/slack/Makefile

clean-backend-dependencies:
	@rm -rf backend/.cache
	@rm -rf backend/.local
	@rm -rf backend/.pytest_cache
	@rm -rf backend/.ruff_cache
	@rm -rf backend/.venv

clean-backend-docker:
	@docker container rm -f nest-backend >/dev/null 2>&1 || true
	@docker container rm -f nest-cache >/dev/null 2>&1 || true
	@docker container rm -f nest-db >/dev/null 2>&1 || true
	@docker container rm -f nest-worker >/dev/null 2>&1 || true
	@docker image rm -f nest-local-backend >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_backend-venv >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_cache-data >/dev/null 2>&1 || true

create-superuser:
	@CMD="python manage.py createsuperuser" $(MAKE) exec-backend-command-it

exec-backend-command:
	@docker exec -i nest-backend $(CMD)

exec-backend-command-it:
	@docker exec -it nest-backend $(CMD) 2>/dev/null

exec-backend-command-e2e:
	@docker exec -it e2e-nest-backend $(CMD)

exec-db-command-it:
	@docker exec -it nest-db $(CMD)

exec-db-command-e2e:
	@docker exec -it e2e-nest-db $(CMD)

clear-cache:
	@CMD="python manage.py clear_cache" $(MAKE) exec-backend-command

collect-static:
	@CMD="python manage.py collectstatic --noinput" $(MAKE) exec-backend-command

django-shell:
	@CMD="python manage.py shell" $(MAKE) exec-backend-command-it

dump-data:
	@echo "Dumping Nest data"
	@CMD="python manage.py dump_data" $(MAKE) exec-backend-command-it

enrich-data: \
	github-enrich-issues \
	owasp-enrich-chapters \
	owasp-enrich-committees \
	owasp-enrich-events \
	owasp-enrich-projects

generate-sitemap:
	@CMD="python manage.py generate_sitemap" $(MAKE) exec-backend-command

index-data:
	@echo "Indexing Nest data"
	@CMD="python manage.py algolia_reindex" $(MAKE) exec-backend-command
	@CMD="python manage.py algolia_update_replicas" $(MAKE) exec-backend-command
	@CMD="python manage.py algolia_update_synonyms" $(MAKE) exec-backend-command

load-data:
	@echo "Loading Nest data"
	@gunzip -c backend/data/nest.sql.gz | docker exec -i nest-db psql -U nest_user_dev -d nest_db_dev

load-data-e2e:
	@echo "Loading Nest e2e data"
	@gunzip -c backend/data/nest.sql.gz | docker exec -i e2e-nest-db psql -U nest_user_e2e -d nest_db_e2e

merge-migrations:
	@CMD="python manage.py makemigrations --merge" $(MAKE) exec-backend-command

migrate:
	@CMD="python manage.py migrate" $(MAKE) exec-backend-command

migrations:
	@CMD="python manage.py makemigrations" $(MAKE) exec-backend-command

purge-data:
	@CMD="python manage.py purge_data" $(MAKE) exec-backend-command

recreate-schema:
	@echo "Recreating Nest schema"
	@CMD="psql -U nest_user_dev -d nest_db_dev -c \
		'DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO nest_user_dev'" \
	  	$(MAKE) exec-db-command-it 2>/dev/null
	@$(MAKE) migrate

restore-backup:
	@echo "Restoring Nest backup"
	@CMD="python manage.py restore_backup" $(MAKE) exec-backend-command

run-backend-e2e:
	@DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-e2e -f docker-compose/e2e.yaml up --build --remove-orphans --abort-on-container-exit backend db

save-backup:
	@echo "Saving Nest backup"
	@CMD="python manage.py dumpdata --natural-primary --natural-foreign --indent=2" $(MAKE) exec-backend-command > backend/data/backup.json
	@gzip backend/data/backup.json

shell-backend:
	@CMD="/bin/sh" $(MAKE) exec-backend-command-it

shell-db:
	@CMD="/bin/sh" $(MAKE) exec-db-command-it

sync-data: \
	update-data \
	enrich-data \
	index-data

test-backend:
	@DOCKER_BUILDKIT=1 docker build \
		--cache-from nest-test-backend \
		-f backend/docker/Dockerfile.test backend \
		-t nest-test-backend
	@docker run \
		-e DJANGO_SETTINGS_MODULE=settings.test \
		--env-file backend/.env.example \
		--rm nest-test-backend pytest

update-backend-dependencies:
	@cd backend && poetry update

update-data: \
	github-update-owasp-organization \
	owasp-scrape-chapters \
	owasp-scrape-committees \
	owasp-scrape-projects \
	github-add-related-repositories \
	github-update-related-organizations \
	github-update-users \
	owasp-aggregate-projects \
	owasp-update-events \
	owasp-sync-posts \
	owasp-update-sponsors \
	slack-sync-data
