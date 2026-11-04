.PHONY: ai-run-agentic-rag ai-update-chapter-chunks ai-update-chapter-context \
	ai-update-committee-chunks ai-update-committee-context ai-update-event-chunks \
	ai-update-event-context ai-update-project-chunks ai-update-project-context \
	ai-update-repository-chunks ai-update-repository-context ai-update-slack-message-chunks \
	ai-update-slack-message-context

ai-run-agentic-rag:
	@echo "Running agentic RAG"
	@CMD="python manage.py ai_run_agentic_rag" $(MAKE) backend-exec-nestbot-command

ai-update-chapter-chunks:
	@echo "Updating chapter chunks"
	@CMD="python manage.py ai_update_chapter_chunks" $(MAKE) backend-exec-nestbot-command

ai-update-chapter-context:
	@echo "Updating chapter context"
	@CMD="python manage.py ai_update_chapter_context" $(MAKE) backend-exec-nestbot-command

ai-update-committee-chunks:
	@echo "Updating committee chunks"
	@CMD="python manage.py ai_update_committee_chunks" $(MAKE) backend-exec-nestbot-command

ai-update-committee-context:
	@echo "Updating committee context"
	@CMD="python manage.py ai_update_committee_context" $(MAKE) backend-exec-nestbot-command

ai-update-event-chunks:
	@echo "Updating event chunks"
	@CMD="python manage.py ai_update_event_chunks" $(MAKE) backend-exec-nestbot-command

ai-update-event-context:
	@echo "Updating event context"
	@CMD="python manage.py ai_update_event_context" $(MAKE) backend-exec-nestbot-command

ai-update-project-chunks:
	@echo "Updating project chunks"
	@CMD="python manage.py ai_update_project_chunks" $(MAKE) backend-exec-nestbot-command

ai-update-project-context:
	@echo "Updating project context"
	@CMD="python manage.py ai_update_project_context" $(MAKE) backend-exec-nestbot-command

ai-update-repository-chunks:
	@echo "Updating repository chunks"
	@CMD="python manage.py ai_update_repository_chunks" $(MAKE) backend-exec-nestbot-command

ai-update-repository-context:
	@echo "Updating repository context"
	@CMD="python manage.py ai_update_repository_context" $(MAKE) backend-exec-nestbot-command

ai-update-slack-message-chunks:
	@echo "Updating Slack message chunks"
	@CMD="python manage.py ai_update_slack_message_chunks" $(MAKE) backend-exec-nestbot-command

ai-update-slack-message-context:
	@echo "Updating Slack message context"
	@CMD="python manage.py ai_update_slack_message_context" $(MAKE) backend-exec-nestbot-command

AI_TEST_ENV_FILE ?= .env.unit-tests

.PHONY: test-ai-evaluation
test-ai-evaluation: ## Run AI evaluation unit tests
ifeq ($(EXEC_MODE),direct)
	@cd backend
	poetry run -- dotenv -f "$(AI_TEST_ENV_FILE)" run --no-override -- \
		pytest tests/unit/apps/ai/evaluation/ -o addopts=''
else
	@$(MAKE) backend-test-unit PYTEST_ARGS="tests/unit/apps/ai/evaluation/ -o addopts=''"
endif
