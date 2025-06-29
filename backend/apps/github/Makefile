github-enrich-issues:
	@echo "Enriching GitHub issues"
	@CMD="python manage.py github_enrich_issues" $(MAKE) exec-backend-command

github-match-users:
	@CMD="python manage.py github_match_users $(MATCH_MODEL)" $(MAKE) exec-backend-command

github-update-owasp-organization:
	@echo "Updating OWASP GitHub organization"
	@CMD="python manage.py github_update_owasp_organization" $(MAKE) exec-backend-command

github-update-owasp-related-organizations:
	@echo "Updating external OWASP GitHub organizations"
	@CMD="python manage.py github_update_external_organizations" $(MAKE) exec-backend-command

github-update-project-related-repositories:
	@echo "Updating OWASP project related GitHub repositories"
	@CMD="python manage.py github_update_project_related_repositories" $(MAKE) exec-backend-command

github-update-users:
	@echo "Updating GitHub users"
	@CMD="python manage.py github_update_users" $(MAKE) exec-backend-command
