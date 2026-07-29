.PHONY: slack-check-invite-link slack-export-data slack-match-owasp-channels \
	slack-set-conversation-sync-messages-flags slack-sync-data slack-sync-messages

slack-check-invite-link:
	@echo "Checking Slack invite link usage"
	@CMD="python manage.py slack_check_invite_link" $(MAKE) backend-exec-command

slack-export-data:
	@echo "Exporting Slack data"
	@CMD="python manage.py dumpdata \
		slack.Conversation \
		slack.Member \
		slack.Message \
		slack.Workspace \
		--indent=4 \
		--natural-foreign \
		--natural-primary -o data/slack-data.json" $(MAKE) backend-exec-command
	@CMD="sed -E -i 's/(\"[^\"]*email\"): *\"([^\"]|\\\")*\"/\1: \"\"/g' data/slack-data.json" $(MAKE) backend-exec-command
	@CMD="gzip data/slack-data.json" $(MAKE) backend-exec-command

slack-match-owasp-channels:
	@echo "Matching Slack channels to OWASP chapters, committees, and projects"
	@CMD="python manage.py slack_match_owasp_channels" $(MAKE) backend-exec-command

slack-set-conversation-sync-messages-flags:
	@echo "Setting conversation sync messages flags"
	@CMD="python manage.py slack_set_conversation_sync_messages_flags" $(MAKE) backend-exec-command

slack-sync-data:
	@echo "Syncing Slack data"
	@CMD="python manage.py slack_sync_data" $(MAKE) backend-exec-command

slack-sync-messages:
	@echo "Syncing Slack messages"
	@CMD="python manage.py slack_sync_messages" $(MAKE) backend-exec-command
