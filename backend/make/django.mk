.PHONY: create-superuser migrate migration clear-cache collect-static \
	merge-migrations migrations migrations-empty backend-django-clear-cache \
	backend-django-collect-static backend-django-create-superuser \
	backend-django-merge-migrations backend-django-migrate backend-django-migrations \
	backend-django-migrations-empty backend-django-shell

create-superuser: ## Create a Django admin superuser
	@$(MAKE) backend-django-create-superuser

migrate: ## Run database migrations
	@$(MAKE) backend-django-migrate

migration: ## Create database migrations
	@$(MAKE) backend-django-migrations

clear-cache:
	@$(MAKE) backend-django-clear-cache

collect-static:
	@$(MAKE) backend-django-collect-static

merge-migrations:
	@$(MAKE) backend-django-merge-migrations

migrations:
	@$(MAKE) backend-django-migrations

migrations-empty:
	@$(MAKE) backend-django-migrations-empty

# Implementation targets.

backend-django-clear-cache:
	@CMD="python manage.py clear_cache" $(MAKE) backend-exec-command

backend-django-collect-static:
	@CMD="python manage.py collectstatic --noinput" $(MAKE) backend-exec-command

backend-django-create-superuser:
	@CMD="python manage.py createsuperuser" $(MAKE) backend-exec-command-it

backend-django-merge-migrations:
	@CMD="python manage.py makemigrations --merge" $(MAKE) backend-exec-command

backend-django-migrate:
	@CMD="python manage.py migrate" $(MAKE) backend-exec-command

backend-django-migrations:
	@CMD="python manage.py makemigrations" $(MAKE) backend-exec-command

backend-django-migrations-empty:
	@CMD="python manage.py makemigrations --empty $(APP_NAME)" $(MAKE) backend-exec-command

backend-django-shell:
	@CMD="python manage.py shell" $(MAKE) backend-exec-command-it
