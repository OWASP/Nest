FROM node:24.20-alpine3.23@sha256:0388af2af070cd4736a1567cfed02469ba117848845b4165d87a333edb53d2ca AS base

# Install dependencies and build the project.
FROM base AS builder
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine
# to understand why libc6-compat might be needed.
ENV APK_CACHE_DIR="/app/.cache/apk" \
    APK_SYMLINK_DIR="/etc/apk/cache" \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    FORCE_COLOR=1 \
    NPM_CONFIG_CACHE="/app/.npm" \
    PNPM_CONFIG_FETCH_RETRIES=5 \
    PNPM_CONFIG_FETCH_TIMEOUT=30000 \
    PNPM_HOME="/pnpm"

ARG ENV_FILE=.env
ARG NEXT_PUBLIC_E2E_BACKEND_BASE_URL

ENV PATH="$PNPM_HOME:$PATH" \
    NEXT_PUBLIC_E2E_BACKEND_BASE_URL=${NEXT_PUBLIC_E2E_BACKEND_BASE_URL}

RUN mkdir -p ${APK_CACHE_DIR} && \
    ln -fns ${APK_CACHE_DIR} ${APK_SYMLINK_DIR}

RUN --mount=type=cache,target=${APK_CACHE_DIR} \
    apk --no-cache update && \
    apk --no-cache add libc6-compat

WORKDIR /app

COPY --chmod=444 package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    corepack install && corepack enable pnpm && \
    pnpm install --frozen-lockfile

COPY --chmod=444 next.config.ts postcss.config.js tailwind.config.mjs tsconfig.json ./
COPY --chmod=444 ${ENV_FILE} ./.env
COPY --chmod=555 public public
COPY --chmod=555 src src

ARG FORCE_STANDALONE
ENV FORCE_STANDALONE=$FORCE_STANDALONE

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
ENV NEXT_TELEMETRY_DISABLED=1
RUN --mount=type=secret,id=RELEASE_VERSION \
    --mount=type=secret,id=SENTRY_AUTH_TOKEN \
    NEXT_SENTRY_AUTH_TOKEN="$(cat /run/secrets/SENTRY_AUTH_TOKEN 2>/dev/null || true)" && \
    export NEXT_SENTRY_AUTH_TOKEN && \
    RELEASE_VERSION="$(cat /run/secrets/RELEASE_VERSION 2>/dev/null || true)" && \
    export RELEASE_VERSION && \
    pnpm run build

# Production image: Alpine OS + Node binary only (no npm/corepack/yarn).
FROM alpine:3.24@sha256:28bd5fe8b56d1bd048e5babf5b10710ebe0bae67db86916198a6eec434943f8b AS runner

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# libstdc++ is required by the Node binary (ldd); busybox wget/shell cover ECS health checks.
RUN apk --no-cache upgrade && \
    apk --no-cache add libstdc++=15.2.0-r2 && \
    addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 -G nodejs nextjs && \
    rm -rf /var/cache/apk/* /var/tmp/* /tmp/*

COPY --from=base --chmod=555 /usr/local/bin/node /usr/local/bin/node

WORKDIR /app

# Copying files with root as owner, so that executing user cannot change the container.
COPY --from=builder --chown=root:root --chmod=555 /app/public public

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/pages/api-reference/config/next-config-js/output
COPY --from=builder --chown=root:root --chmod=555  /app/.next/standalone .

# Create cache directory and assign ownership to nextjs user with write permission, so that cache can be stored.
RUN mkdir -p /app/.next/cache && chown -R nextjs:nodejs /app/.next/cache && chmod -R 755 /app/.next/cache && rm .env
COPY --from=builder --chown=root:root --chmod=555 /app/.next/static .next/static

USER nextjs

EXPOSE 3000

ENV HOSTNAME="0.0.0.0"
ENV PORT=3000

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/config/next-config-js/output
CMD ["node", "server.js"]
