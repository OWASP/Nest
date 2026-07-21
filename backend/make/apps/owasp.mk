.PHONY: owasp-add-project-custom-tags owasp-aggregate-entity-contributions \
	owasp-aggregate-member-contributions owasp-aggregate-projects owasp-create-project-metadata-file \
	owasp-enrich-chapters owasp-enrich-committees owasp-enrich-events owasp-enrich-projects \
	owasp-generate-community-snapshot-video owasp-process-snapshots owasp-scrape-chapters \
	owasp-scrape-committees owasp-scrape-projects owasp-sync-posts owasp-update-events \
	owasp-update-leaders owasp-update-project-health-metrics owasp-update-project-health-requirements \
	owasp-update-project-health-scores owasp-update-sponsors

owasp-add-project-custom-tags:
	@echo "Adding project custom tags from $(FILE)"
	@CMD="python manage.py add_project_custom_tags $(FILE)" $(MAKE) backend-exec-command

owasp-aggregate-entity-contributions:
	@echo "Aggregating OWASP contributions"
	@CMD="python manage.py owasp_aggregate_entity_contributions --entity-type chapter" $(MAKE) backend-exec-command
	@CMD="python manage.py owasp_aggregate_entity_contributions --entity-type project" $(MAKE) backend-exec-command

owasp-aggregate-member-contributions:
	@echo "Aggregating OWASP community member contributions"
	@CMD="python manage.py owasp_aggregate_member_contributions" $(MAKE) backend-exec-command

owasp-aggregate-projects:
	@echo "Aggregating OWASP projects"
	@CMD="python manage.py owasp_aggregate_projects" $(MAKE) backend-exec-command

owasp-create-project-metadata-file:
	@echo "Generating metadata"
	@CMD="python manage.py owasp_create_project_metadata_file $(entity_key)" $(MAKE) backend-exec-command

owasp-enrich-chapters:
	@echo "Enriching OWASP chapters"
	@CMD="python manage.py owasp_enrich_chapters" $(MAKE) backend-exec-command

owasp-enrich-committees:
	@echo "Enriching OWASP committees"
	@CMD="python manage.py owasp_enrich_committees" $(MAKE) backend-exec-command

owasp-enrich-events:
	@echo "Enriching OWASP events"
	@CMD="python manage.py owasp_enrich_events" $(MAKE) backend-exec-command

owasp-enrich-projects:
	@echo "Enriching OWASP projects"
	@CMD="python manage.py owasp_enrich_projects" $(MAKE) backend-exec-command

owasp-generate-community-snapshot-video:
	@docker build \
		-f docker/backend/Dockerfile \
		--target video \
		backend/ \
		-t nest-snapshot-video
	@mkdir -p backend/generated_videos
	@docker run \
		--env-file backend/.env \
		--mount type=bind,src="$(CURDIR)/backend/generated_videos",dst=/home/owasp/generated_videos \
		--network nest-local_nest-network \
		--rm \
		nest-snapshot-video \
		python manage.py owasp_generate_community_snapshot_video $(snapshot_key) /home/owasp/generated_videos

SNAPSHOT_FREQUENCY ?= weekly

owasp-create-snapshot:
	@echo "Creating OWASP community snapshot"
	@CMD="python manage.py owasp_create_snapshot --frequency $(SNAPSHOT_FREQUENCY)" $(MAKE) exec-backend-command

owasp-process-snapshots:
	@echo "Processing OWASP snapshots"
	@CMD="python manage.py owasp_process_snapshots" $(MAKE) backend-exec-command

owasp-scrape-chapters:
	@echo "Scraping OWASP site chapters data"
	@CMD="python manage.py owasp_scrape_chapters" $(MAKE) backend-exec-command

owasp-scrape-committees:
	@echo "Scraping OWASP site committees data"
	@CMD="python manage.py owasp_scrape_committees" $(MAKE) backend-exec-command

owasp-scrape-projects:
	@echo "Scraping OWASP site projects data"
	@CMD="python manage.py owasp_scrape_projects" $(MAKE) backend-exec-command

owasp-sync-posts:
	@CMD="python manage.py owasp_sync_posts" $(MAKE) backend-exec-command

owasp-update-events:
	@echo "Getting OWASP events data"
	@CMD="python manage.py owasp_update_events" $(MAKE) backend-exec-command

owasp-update-leaders:
	@CMD="python manage.py owasp_update_leaders $(MATCH_MODEL)" $(MAKE) backend-exec-command

owasp-update-project-health-metrics:
	@echo "Updating OWASP project health metrics"
	@CMD="python manage.py owasp_update_project_health_metrics" $(MAKE) backend-exec-command

owasp-update-project-health-requirements:
	@echo "Updating OWASP project health requirements"
	@CMD="python manage.py owasp_update_project_health_requirements" $(MAKE) backend-exec-command

owasp-update-project-health-scores:
	@echo "Updating OWASP project health scores"
	@CMD="python manage.py owasp_update_project_health_scores" $(MAKE) backend-exec-command

owasp-update-sponsors:
	@echo "Getting OWASP sponsors data"
	@CMD="python manage.py owasp_update_sponsors" $(MAKE) backend-exec-command
