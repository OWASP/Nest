.PHONY: mentorship-sync-issue-levels mentorship-sync-module-issues mentorship-update-comments

mentorship-sync-issue-levels:
	@echo "Syncing module issue levels"
	@CMD="python manage.py mentorship_sync_issue_levels" $(MAKE) backend-exec-command

mentorship-sync-module-issues:
	@echo "Syncing module issues"
	@CMD="python manage.py mentorship_sync_module_issues" $(MAKE) backend-exec-command

mentorship-update-comments:
	@echo "Updating issue comments"
	@CMD="python manage.py mentorship_update_comments" $(MAKE) backend-exec-command
