nest-update-staff-badge:
	@echo "Updating OWASP Staff badges"
	@CMD="python manage.py nest_update_staff_badge" $(MAKE) exec-backend-command

nest-update-project-leader-badge:
	@echo "Updating OWASP Project Leader badges"
	@CMD="python manage.py nest_update_project_leader_badge" $(MAKE) exec-backend-command

nest-update-badges: \
	nest-update-staff-badge \
	nest-update-project-leader-badge \
