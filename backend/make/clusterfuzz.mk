.PHONY: test-backend-cluster-fuzz-lite backend-clusterfuzz-build backend-clusterfuzz-build-fuzzers \
	backend-clusterfuzz-clean backend-clusterfuzz-test

test-backend-cluster-fuzz-lite: ## Run ClusterFuzzLite fuzz targets
	@$(MAKE) backend-clusterfuzz-test

# Implementation targets.

CFL_DOCKERFILE ?= .clusterfuzzlite/Dockerfile
CFL_IMAGE ?= nest-cluster-fuzz-lite
CFL_OUT_DIR ?= $(CURDIR)/.clusterfuzzlite/out
CFL_PLATFORM ?= linux/amd64
CFL_SANITIZER ?= address
CFL_SECONDS ?= 60
CFL_TARGETS ?= text query_parser

backend-clusterfuzz-build:
	@docker build \
		--platform $(CFL_PLATFORM) \
		-f $(CFL_DOCKERFILE) \
		-t $(CFL_IMAGE) \
		$(CURDIR)

backend-clusterfuzz-build-fuzzers: backend-clusterfuzz-build
	@mkdir -p $(CFL_OUT_DIR)
	@docker run \
		--platform $(CFL_PLATFORM) \
		--rm \
		-e ARCH=x86_64 \
		-e FUZZING_ENGINE=libfuzzer \
		-e OUT=/out \
		-e SANITIZER=$(CFL_SANITIZER) \
		-v $(CFL_OUT_DIR):/out \
		$(CFL_IMAGE) \
		bash build.sh

backend-clusterfuzz-clean:
	@rm -rf $(CFL_OUT_DIR)
	@docker image rm -f $(CFL_IMAGE) >/dev/null 2>&1 || true

backend-clusterfuzz-test: backend-clusterfuzz-build-fuzzers
	@for target in $(CFL_TARGETS); do \
		echo "Running ClusterFuzzLite target: $$target ($(CFL_SECONDS)s)"; \
		docker run \
		--platform $(CFL_PLATFORM) \
		--rm \
		-e ARCH=x86_64 \
		-e FUZZING_ENGINE=libfuzzer \
		-e OUT=/out \
		-e SANITIZER=$(CFL_SANITIZER) \
		-v $(CFL_OUT_DIR):/out \
		$(CFL_IMAGE) \
		/out/$$target -max_total_time=$(CFL_SECONDS); \
	done
