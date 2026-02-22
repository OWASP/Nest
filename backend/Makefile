include backend/apps/ai/Makefile
include backend/apps/github/Makefile
include backend/apps/mentorship/Makefile
include backend/apps/nest/Makefile
include backend/apps/owasp/Makefile
include backend/apps/slack/Makefile

SHELL := /bin/bash

.PHONY: sbom-backend-image

build-backend-local-image:
	@DOCKER_BUILDKIT=1 docker build \
		--no-cache \
		-f docker/backend/Dockerfile \
		-t nest-backend-local \
		backend

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
	@docker image rm -f nest-backend:base >/dev/null 2>&1 || true
	@docker image rm -f nest-local-backend >/dev/null 2>&1 || true
	@docker image rm -f nest-snapshot-video >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_backend-venv >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_cache-data >/dev/null 2>&1 || true

create-superuser:
	@CMD="python manage.py createsuperuser" $(MAKE) exec-backend-command-it

exec-backend-command:
	@docker exec -i nest-backend $(CMD)

exec-backend-command-it:
	@docker exec -it nest-backend $(CMD) 2>/dev/null

exec-backend-command-e2e:
	@docker exec -i e2e-nest-backend $(CMD)

exec-backend-command-e2e-it:
	@docker exec -it e2e-nest-backend $(CMD)

exec-backend-command-fuzz:
	@docker exec -i fuzz-nest-backend $(CMD)

exec-backend-command-fuzz-it:
	@docker exec -it fuzz-nest-backend $(CMD)

exec-db-command:
	@docker exec -i nest-db $(CMD)

exec-db-command-it:
	@docker exec -it nest-db $(CMD)

exec-db-command-e2e:
	@docker exec -i e2e-nest-db $(CMD)

exec-db-command-e2e-it:
	@docker exec -it e2e-nest-db $(CMD)

exec-db-command-fuzz:
	@docker exec -i fuzz-nest-db $(CMD)

exec-db-command-fuzz-it:
	@docker exec -it fuzz-nest-db $(CMD)

exec-db-command-staging:
	@docker exec -i staging-nest-db $(CMD)

exec-db-command-staging-it:
	@docker exec -it staging-nest-db $(CMD)

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
	@echo "Truncating content_type table"
	@CMD="psql -U nest_user_dev -d nest_db_dev -c \"TRUNCATE django_content_type CASCADE;\"" $(MAKE) exec-db-command
	@echo "Loading Nest data"
	@CMD="pg_restore -U nest_user_dev -d nest_db_dev < ./backend/data/nest.dump" $(MAKE) exec-db-command

load-data-e2e:
	@echo "Truncating content_type table"
	@CMD="psql -U nest_user_e2e -d nest_db_e2e -c \"TRUNCATE django_content_type CASCADE;\"" $(MAKE) exec-db-command-e2e
	@echo "Loading Nest e2e data"
	@CMD="pg_restore -U nest_user_e2e -d nest_db_e2e < ./backend/data/nest.dump" $(MAKE) exec-db-command-e2e

load-data-fuzz:
	@echo "Truncating content_type table"
	@CMD="psql -U nest_user_fuzz -d nest_db_fuzz -c \"TRUNCATE django_content_type CASCADE;\"" $(MAKE) exec-db-command-fuzz
	@echo "Loading Nest fuzz data"
	@CMD="pg_restore -U nest_user_fuzz -d nest_db_fuzz < ./backend/data/nest.dump" $(MAKE) exec-db-command-fuzz

load-data-staging:
	@echo "Truncating content_type table"
	@CMD="psql -U nest_user_staging -d nest_db_staging -c \"TRUNCATE django_content_type CASCADE;\"" $(MAKE) exec-db-command-staging
	@echo "Loading Nest staging data"
	@CMD="pg_restore -U nest_user_staging -d nest_db_staging < ./backend/data/nest.dump" $(MAKE) exec-db-command-staging

merge-migrations:
	@CMD="python manage.py makemigrations --merge" $(MAKE) exec-backend-command

migrate:
	@CMD="python manage.py migrate" $(MAKE) exec-backend-command

migrations:
	@CMD="python manage.py makemigrations" $(MAKE) exec-backend-command

migrations-empty:
	@CMD="python manage.py makemigrations --empty $(APP_NAME)" $(MAKE) exec-backend-command

purge-data:
	@CMD="python manage.py purge_data" $(MAKE) exec-backend-command

purge-data-e2e:
	@CMD="python manage.py purge_data" $(MAKE) exec-backend-command-e2e

purge-data-fuzz:
	@CMD="python manage.py purge_data" $(MAKE) exec-backend-command-fuzz

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
	docker compose --project-name nest-e2e -f docker-compose/e2e/compose.yaml up --build --remove-orphans --abort-on-container-exit backend db cache

run-backend-fuzz:
	@COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml up --build --remove-orphans --abort-on-container-exit backend db cache

save-backup:
	@echo "Saving Nest backup"
	@CMD="python manage.py dumpdata --natural-primary --natural-foreign --indent=2" $(MAKE) exec-backend-command > backend/data/backup.json
	@gzip backend/data/backup.json

# vars (defaults for local dev)
BACKEND_IMAGE_NAME ?= nest-backend-local
IMAGE_SCANNERS ?= misconfig,secret,vuln

security-scan-backend-image:
	@if [ "$(BACKEND_IMAGE_NAME)" = "nest-backend-local" ]; then \
		$(MAKE) build-backend-local-image; \
	fi
	@echo "Scanning image: $(BACKEND_IMAGE_NAME)..."
	@docker run \
		--rm \
		-e TRIVY_SCANNERS="$(IMAGE_SCANNERS)" \
		-v $(CURDIR)/trivyignore.yaml:/trivyignore.yaml:ro \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/trivy.yaml:/trivy.yaml:ro \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		image --config /trivy.yaml $(BACKEND_IMAGE_NAME)

SBOM_VERSION := $(if $(RELEASE_VERSION),$(RELEASE_VERSION),local)

sbom-backend-image:
	@if [ "$(BACKEND_IMAGE_NAME)" = "nest-backend-local" ]; then \
		$(MAKE) build-backend-local-image; \
	fi
	@echo "Generating SBOM for image: $(BACKEND_IMAGE_NAME)..."
	@docker run \
		--rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/.trivy-cache:/root/.cache/trivy \
		-v $(CURDIR):/work \
		$$(grep -E '^FROM aquasec/trivy:' docker/trivy/Dockerfile | sed 's/^FROM //') \
		image \
		--format cyclonedx \
		--output /work/backend-sbom-$(SBOM_VERSION).cdx.json \
		$(BACKEND_IMAGE_NAME)

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
		-f docker/backend/Dockerfile.test backend \
		-t nest-test-backend
	@docker run \
		-e DJANGO_SETTINGS_MODULE=settings.test \
		--env-file backend/.env.example \
		--rm nest-test-backend pytest

test-fuzz:
	@docker container rm -f fuzz-nest-db >/dev/null 2>&1 || true
	@docker volume rm -f nest-fuzz_fuzz-db-data >/dev/null 2>&1 || true
	@COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml up --build --remove-orphans --abort-on-container-exit db cache backend data-loader
	@echo "Running REST API fuzz tests..."
	@COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml up --build --remove-orphans --abort-on-container-exit db backend rest
	@echo "Running GraphQL fuzz tests..."
	@COMPOSE_BAKE=true DOCKER_BUILDKIT=1 \
	docker compose --project-name nest-fuzz -f docker-compose/fuzz/compose.yaml up --build --remove-orphans --abort-on-container-exit db cache backend graphql

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
	owasp-aggregate-entity-contributions \
	owasp-aggregate-member-contributions \
	owasp-update-events \
	owasp-sync-posts \
	owasp-update-sponsors \
	slack-sync-data
