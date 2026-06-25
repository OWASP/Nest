FROM node:24.17-alpine3.23@sha256:7c70d1235c0b4c2bc9eeed5393d19f1bbdde6885ba0d58ba62bb385d7b0f3ff1

WORKDIR /opt/node

ENV PNPM_HOME="/pnpm"
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    NPM_CONFIG_CACHE="/nest/.npm" \
    PATH="$PNPM_HOME:$PATH" \
    PNPM_CONFIG_FETCH_RETRIES=5 \
    PNPM_CONFIG_FETCH_TIMEOUT=30000

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    corepack install && corepack enable pnpm && \
    pnpm install --frozen-lockfile

WORKDIR /nest

USER node

ENTRYPOINT ["/opt/node/node_modules/.bin/cspell"]
