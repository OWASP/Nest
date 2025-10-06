github-add-related-repositories:
	@echo "Adding OWASP related repositories"
	@CMD="python manage.py github_add_related_repositories" $(MAKE) exec-backend-command

github-enrich-issues:
	@echo "Enriching GitHub issues"
	@CMD="python manage.py github_enrich_issues" $(MAKE) exec-backend-command

github-update-owasp-organization:
	@echo "Updating OWASP GitHub organization"
	@CMD="python manage.py github_update_owasp_organization" $(MAKE) exec-backend-command

github-update-related-organizations:
	@echo "Updating OWASP related organizations"
	@CMD="python manage.py github_update_related_organizations" $(MAKE) exec-backend-command

github-update-users:
	@echo "Updating GitHub users"
	@CMD="python manage.py github_update_users" $(MAKE) exec-backend-command

github-update-pull-requests:
	@echo "Linking pull requests to issues using closing keywords"
	@CMD="python manage.py github_update_pull_requests" $(MAKE) exec-backend-command
