FROM node:lts-alpine

WORKDIR /opt/node

RUN npm install -g pnpm

COPY pnpm-lock.yaml package.json ./

RUN pnpm install

WORKDIR /nest

ENTRYPOINT ["/opt/node/node_modules/.bin/cspell"]
