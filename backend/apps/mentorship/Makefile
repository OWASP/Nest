mentorship-sync-issue-levels:
	@CMD="python manage.py sync_issue_levels" $(MAKE) exec-backend-command

mentorship-sync-module-issues:
	@CMD="python manage.py sync_module_issues" $(MAKE) exec-backend-command

mentorship-update-comments:
	@echo "Syncing Github Comments related to issues"
	@CMD="python manage.py mentorship_update_comments" $(MAKE) exec-backend-command
