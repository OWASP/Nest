nest-update-project-leader-badges:
	@echo "Updating OWASP Project Leader badges"
	@CMD="python manage.py nest_update_project_leader_badges" $(MAKE) exec-backend-command

nest-update-staff-badges:
	@echo "Updating OWASP Staff badges"
	@CMD="python manage.py nest_update_staff_badges" $(MAKE) exec-backend-command

nest-update-badges: \
	nest-update-project-leader-badges \
	nest-update-staff-badges
