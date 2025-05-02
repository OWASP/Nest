FROM node:23-alpine

WORKDIR /opt/node

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH" \
    NPM_CONFIG_RETRY=5 \
    NPM_CONFIG_TIMEOUT=30000

COPY package.json pnpm-lock.yaml ./

RUN npm install --ignore-scripts -g pnpm

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile --ignore-scripts

WORKDIR /nest

ENTRYPOINT ["/opt/node/node_modules/.bin/cspell"]

USER node
