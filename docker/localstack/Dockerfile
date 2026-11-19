FROM localstack/localstack:2026.10.4@sha256:2290500d7398e6458544fab2f49aaf170b81a1006ee69067e8e7fc59b810a824

# The upstream image does not include curl. The compose health check calls it.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl=8.14.1-2+deb13u7 && \
    rm -rf /var/lib/apt/lists/*
