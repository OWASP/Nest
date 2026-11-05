.PHONY: backend-clean-dependencies backend-clean-docker

# Implementation targets.

backend-clean-dependencies:
	@rm -rf backend/.cache
	@rm -rf backend/.local
	@rm -rf backend/.pytest_cache
	@rm -rf backend/.ruff_cache
	@rm -rf backend/.venv

backend-clean-docker:
	@docker container rm -f nest-backend >/dev/null 2>&1 || true
	@docker container rm -f nest-cache >/dev/null 2>&1 || true
	@docker container rm -f nest-db >/dev/null 2>&1 || true
	@docker container rm -f nest-worker >/dev/null 2>&1 || true
	@docker image rm -f nest-local-backend >/dev/null 2>&1 || true
	@docker image rm -f nest-snapshot-video >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_backend-venv >/dev/null 2>&1 || true
	@docker volume rm -f nest-local_cache-data >/dev/null 2>&1 || true
