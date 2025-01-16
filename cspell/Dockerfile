FROM node:lts-alpine

WORKDIR /opt/node

COPY package-lock.json package.json ./

RUN npm install

WORKDIR /nest

ENTRYPOINT ["/opt/node/node_modules/.bin/cspell"]
