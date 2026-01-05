FROM node:24-alpine

WORKDIR /opt/node

ENV PNPM_HOME="/pnpm"
ENV NPM_CONFIG_RETRY=5 \
    NPM_CACHE="/nest/.npm" \
    NPM_CONFIG_TIMEOUT=30000 \
    PATH="$PNPM_HOME:$PATH"

RUN --mount=type=cache,target=${NPM_CACHE} \
    npm install --ignore-scripts -g pnpm --cache ${NPM_CACHE}

COPY package.json pnpm-lock.yaml ./

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile --ignore-scripts

WORKDIR /nest

ENTRYPOINT ["/opt/node/node_modules/.bin/cspell"]

USER node
