slack-export-data:
	@echo "Exporting Slack data"
	@CMD="python manage.py dumpdata \
		slack.Conversation \
		slack.Member \
		slack.Message \
		slack.Workspace \
		--indent=4 \
		--natural-foreign \
		--natural-primary -o data/slack-data.json" $(MAKE) exec-backend-command
	@CMD="sed -E -i 's/\"email\": *\"([^\"]|\\\")*\"/\"email\": \"\"/g' data/slack-data.json" $(MAKE) exec-backend-command
	@CMD="gzip data/slack-data.json" $(MAKE) exec-backend-command


slack-set-conversation-sync-messages-flags:
	@echo "Setting conversation sync messages flags"
	@CMD="python manage.py slack_set_conversation_sync_messages_flags" $(MAKE) exec-backend-command

slack-sync-data:
	@echo "Syncing Slack data"
	@CMD="python manage.py slack_sync_data" $(MAKE) exec-backend-command

slack-sync-messages:
	@echo "Syncing Slack messages"
	@CMD="python manage.py slack_sync_messages" $(MAKE) exec-backend-command
