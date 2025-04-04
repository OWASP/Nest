FROM node:22-alpine AS builder

WORKDIR /app

COPY --chmod=444 package.json pnpm-lock.yaml ./
RUN npm install --ignore-scripts -g pnpm && \
    pnpm install --ignore-scripts

COPY .env .env
COPY components.json tailwind.config.js tsconfig.json vite.config.ts ./
COPY index.html index.html
COPY public public
COPY src src

RUN pnpm run build

FROM nginx:stable-alpine

COPY --from=builder --chmod=555 /app/dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
RUN chmod -R a-w /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
