FROM node:24.16-alpine3.23@sha256:2bdb65ed1dab192432bc31c95f94155ca5ad7fc1392fb7eb7526ab682fa5bf14

WORKDIR /opt/node

ENV PNPM_HOME="/pnpm"
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    NPM_CONFIG_RETRY=5 \
    NPM_CONFIG_CACHE="/nest/.npm" \
    NPM_CONFIG_TIMEOUT=30000 \
    PATH="$PNPM_HOME:$PATH"

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    corepack install && corepack enable pnpm && \
    pnpm install --frozen-lockfile --ignore-scripts

WORKDIR /nest

USER node

ENTRYPOINT ["/opt/node/node_modules/.bin/cspell"]
