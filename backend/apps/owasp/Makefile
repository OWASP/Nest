owasp-aggregate-projects:
	@echo "Aggregating OWASP projects"
	@CMD="python manage.py owasp_aggregate_projects" $(MAKE) exec-backend-command

owasp-create-project-metadata-file:
	@echo "Generating metadata"
	@CMD="python manage.py owasp_create_project_metadata_file $(entity_key)" $(MAKE) exec-backend-command

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

owasp-update-leaders:
	@CMD="python manage.py owasp_update_leaders $(MATCH_MODEL)" $(MAKE) exec-backend-command

owasp-update-project-health-metrics:
	@echo "Updating OWASP project health metrics"
	@CMD="python manage.py owasp_update_project_health_metrics" $(MAKE) exec-backend-command

owasp-update-project-health-requirements:
	@echo "Updating OWASP project health requirements"
	@CMD="python manage.py owasp_update_project_health_requirements" $(MAKE) exec-backend-command

owasp-update-project-health-scores:
	@echo "Updating OWASP project health scores"
	@CMD="python manage.py owasp_update_project_health_scores" $(MAKE) exec-backend-command

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

owasp-sync-awards:
	@echo "Syncing OWASP awards data"
	@CMD="python manage.py owasp_sync_awards" $(MAKE) exec-backend-command
