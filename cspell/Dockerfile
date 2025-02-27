FROM node:lts-alpine

WORKDIR /opt/node

COPY package.json pnpm-lock.yaml ./

RUN npm install -g pnpm && \
    pnpm install

WORKDIR /nest

ENTRYPOINT ["/opt/node/node_modules/.bin/cspell"]
