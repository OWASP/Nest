FROM localstack/localstack:2026.10.6@sha256:f94401988db4c01a5b2634d37d698a9b11c93f74c1ad0f7a8849f5ebd73dcbdc

# The upstream image does not include curl. The compose health check calls it.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl=8.14.1-2+deb13u7 && \
    rm -rf /var/lib/apt/lists/*
