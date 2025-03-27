test-schema:
	@DOCKER_BUILDKIT=1 docker build \
		--cache-from nest-test-schema \
		-f schema/docker/Dockerfile.test schema \
		-t nest-test-schema
	@docker run nest-test-schema pytest

update-schema-dependencies:
	cd schema && poetry update
