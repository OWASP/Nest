test-schema:
	@docker build -f schema/Dockerfile.test schema -t nest-test-schema
	@docker run nest-test-schema pytest
