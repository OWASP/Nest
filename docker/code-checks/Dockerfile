# Version pin lives in docker/terraform/Dockerfile.
# hadolint ignore=DL3006
FROM terraform AS terraform
FROM ghcr.io/astral-sh/uv:0.11.25@sha256:1e3808aa9023d0980e7c15b1fa7c1ac16ff35925780cf5c459858b2d693f01a9 AS uv
FROM ghcr.io/terraform-linters/tflint:v0.63.1@sha256:890e37827d7b5e400f26137c5189c7efa581365fe9299b5b9814e5148d5978b9 AS tflint
FROM node:24.18-alpine3.23@sha256:595398b0081eacda8e1c4c5b97b76cd1020e4d58a8ebcb4843b9bca1e79e7436 AS node

FROM node AS node-deps

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    PNPM_HOME="/pnpm" \
    PATH="/pnpm:$PATH" \
    PNPM_CONFIG_FETCH_RETRIES=5 \
    PNPM_CONFIG_FETCH_TIMEOUT=30000

WORKDIR /opt/code-checks
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN corepack install && corepack enable pnpm
RUN --mount=type=cache,id=pnpm-code-checks-root,target=/pnpm/store \
    pnpm install --frozen-lockfile

WORKDIR /opt/code-checks/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm-code-checks-frontend,target=/pnpm/store \
    pnpm install --frozen-lockfile

WORKDIR /opt/code-checks/cspell
COPY cspell/package.json cspell/pnpm-lock.yaml cspell/pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm-code-checks-cspell,target=/pnpm/store \
    pnpm install --frozen-lockfile

FROM node AS code-checks

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    FORCE_COLOR=1 \
    PATH="/opt/pre-commit/bin:/nest/node_modules/.bin:/nest/cspell/node_modules/.bin:/usr/local/bin:$PATH" \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PNPM_HOME="/pnpm" \
    PRE_COMMIT_HOME="/tmp/pre-commit" \
    PYTHONUNBUFFERED=1 \
    TF_PLUGIN_CACHE_DIR="/tmp/terraform-plugin-cache" \
    TFLINT_PLUGIN_DIR="/tmp/tflint/plugins" \
    UV_PYTHON_INSTALL_DIR="/usr/local"

RUN apk --no-cache upgrade && \
    apk --no-cache add \
        bash \
        docker-cli \
        git \
        libffi \
        libgcc \
        libstdc++ \
        sqlite-libs && \
    mkdir -p \
        "${PRE_COMMIT_HOME}" \
        "${TF_PLUGIN_CACHE_DIR}" \
        "${TFLINT_PLUGIN_DIR}" \
        /nest/frontend \
        /nest/cspell

COPY --from=uv /uv /usr/local/bin/uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv python install 3.13 && \
    uv venv /opt/pre-commit --python 3.13

COPY package.json /tmp/package.json
WORKDIR /tmp
RUN corepack install && corepack enable pnpm && rm -f package.json
WORKDIR /

COPY --from=node-deps /opt/code-checks/node_modules /nest/node_modules
COPY --from=node-deps /opt/code-checks/frontend/node_modules /nest/frontend/node_modules
COPY --from=node-deps /opt/code-checks/cspell/node_modules /nest/cspell/node_modules
COPY --from=terraform --chmod=555 /bin/terraform /usr/local/bin/terraform
COPY --from=tflint --chmod=555 /usr/local/bin/tflint /usr/local/bin/tflint

COPY --chmod=444 backend/requirements/pre-commit.txt /tmp/pre-commit.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /opt/pre-commit --require-hashes --requirement /tmp/pre-commit.txt && \
    rm -f /tmp/pre-commit.txt /usr/local/bin/uv

COPY --chmod=555 docker/code-checks/entrypoint.sh /entrypoint.sh

WORKDIR /nest

# Reason: This is a dev-tool linter, not a production service. Root access is required for IO operations.
# nosemgrep: dockerfile.security.missing-user-entrypoint.missing-user-entrypoint
ENTRYPOINT ["/entrypoint.sh"]
