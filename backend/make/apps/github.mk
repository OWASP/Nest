.PHONY: github-add-related-repositories github-enrich-issues github-update-owasp-organization \
	github-update-pull-requests github-update-related-organizations github-update-users

github-add-related-repositories:
	@echo "Adding OWASP related repositories"
	@CMD="python manage.py github_add_related_repositories" $(MAKE) backend-exec-command

github-enrich-issues:
	@echo "Enriching GitHub issues"
	@CMD="python manage.py github_enrich_issues" $(MAKE) backend-exec-command

github-update-owasp-organization:
	@echo "Updating OWASP GitHub organization"
	@CMD="python manage.py github_update_owasp_organization" $(MAKE) backend-exec-command

github-update-pull-requests:
	@echo "Linking pull requests to issues using closing keywords"
	@CMD="python manage.py github_update_pull_requests" $(MAKE) backend-exec-command

github-update-related-organizations:
	@echo "Updating OWASP related organizations"
	@CMD="python manage.py github_update_related_organizations" $(MAKE) backend-exec-command

github-update-users:
	@echo "Updating GitHub users"
	@CMD="python manage.py github_update_users" $(MAKE) backend-exec-command
