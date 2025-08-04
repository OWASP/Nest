build-owasp-schema-package:
	cd schema && poetry build

bump-owasp-schema-major:
	cd schema && poetry run bump2version major --allow-dirty

bump-owasp-schema-minor:
	cd schema && poetry run bump2version minor --allow-dirty

bump-owasp-schema-patch:
	cd schema && poetry run bump2version patch --allow-dirty

bump-owasp-schema-major-commit:
	cd schema && poetry run bump2version major --commit --tag --allow-dirty

bump-owasp-schema-minor-commit:
	cd schema && poetry run bump2version minor --commit --tag --allow-dirty

bump-owasp-schema-patch-commit:
	cd schema && poetry run bump2version patch --commit --tag --allow-dirty

clean-package:
	cd schema && rm -rf dist/ build/ *.egg-info/

clean-schema-dependencies:
	@rm -rf schema/.venv

install-owasp-schema-package:
	cd schema && poetry install

publish-package:
	cd schema && poetry publish

test-schema:
	@DOCKER_BUILDKIT=1 docker build \
		--cache-from nest-test-schema \
		-f schema/docker/Dockerfile.test . \
		-t nest-test-schema
	@docker run --rm nest-test-schema pytest


update-schema-dependencies:
	cd schema && poetry update
