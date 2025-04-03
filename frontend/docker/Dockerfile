FROM node:22-alpine AS builder

WORKDIR /app

COPY --chmod=444 package.json pnpm-lock.yaml ./
RUN npm install --ignore-scripts -g pnpm && \
    pnpm install --ignore-scripts

COPY --chmod=755 src src
COPY --chmod=755 public public
COPY --chmod=444 tsconfig.json vite.config.ts ./
COPY --chmod=444 .env.example .env
COPY --chmod=444 index.html index.html
COPY --chmod=444 tailwind.config.js ./
COPY --chmod=444 nginx.conf nginx.conf

RUN pnpm run build

FROM nginx:stable-alpine

COPY --from=builder --chmod=555 /app/dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
RUN chmod -R a-w /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
