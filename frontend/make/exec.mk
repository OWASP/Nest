.PHONY: frontend-exec-command frontend-exec-command-it frontend-exec-shell

frontend-exec-command:
	@docker exec -t nest-frontend $(CMD)

frontend-exec-command-it:
	@docker exec -it nest-frontend $(CMD)

frontend-exec-shell:
	@CMD="/bin/sh" $(MAKE) frontend-exec-command-it
