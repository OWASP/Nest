FROM localstack/localstack:2026.10.8@sha256:be800da7b2f20deeebb1a4fef113ff4fc7fa28871cac4de5036a1ac69e22b6dc

# LocalStack installs these dependencies at runtime.
# Install them now to speed up deployment.
RUN . /opt/code/localstack/.venv/bin/activate && \
    python -m localstack.cli.lpm install redis && \
    python -m localstack.cli.lpm install postgres --version 16 && \
    chown -R localstack:localstack /usr/lib/localstack && \
    chmod -R 777 /usr/lib/localstack  # NOSONAR
