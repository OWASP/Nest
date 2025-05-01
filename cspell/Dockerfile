FROM node:23-alpine

WORKDIR /opt/node

COPY package.json pnpm-lock.yaml ./

RUN npm install --ignore-scripts -g pnpm

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile --ignore-scripts

WORKDIR /nest

ENTRYPOINT ["/opt/node/node_modules/.bin/cspell"]

USER node
