FROM node:22 AS builder
WORKDIR /app

ADD package.json pnpm-lock.yaml /app/
ADD src/ /app/src/
ADD public/ /app/public/
ADD tsconfig.json vite.config.js index.html .eslintrc.js /app/

RUN npm install -g pnpm --ignore-scripts && \
    pnpm install --ignore-scripts && \
    pnpm run build && \
    find /app -type f -exec chmod 644 {} \; && \
    find /app -type d -exec chmod 755 {} \;
FROM nginx:stable-alpine
WORKDIR /usr/share/nginx/html
ADD nginx.conf /etc/nginx/conf.d/default.conf
RUN mkdir -p /tmp/build
WORKDIR /tmp
ADD ${DIST_PATH:-/app/dist}/ /usr/share/nginx/html/
RUN chmod -R a-w /usr/share/nginx/html
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
