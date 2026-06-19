FROM node:24.17-alpine3.23@sha256:7c078d435026a97c8ff97b00d70e2f6ec6298a440e25a9485a9af414d5d37009

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
