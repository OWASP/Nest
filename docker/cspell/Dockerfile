FROM node:24.13-alpine3.23

WORKDIR /opt/node

ENV PNPM_HOME="/pnpm"
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    NPM_CONFIG_RETRY=5 \
    NPM_CONFIG_CACHE="/nest/.npm" \
    NPM_CONFIG_TIMEOUT=30000 \
    PATH="$PNPM_HOME:$PATH"

COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    corepack enable && corepack install && \
    pnpm install --frozen-lockfile --ignore-scripts

WORKDIR /nest

USER node

ENTRYPOINT ["/opt/node/node_modules/.bin/cspell"]
