FROM node:24.13-alpine3.23 AS base

# Install dependencies and build the project.
FROM base AS builder

# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine
# to understand why libc6-compat might be needed.
ENV APK_CACHE_DIR="/app/.cache/apk" \
    APK_SYMLINK_DIR="/etc/apk/cache" \
    FORCE_COLOR=1 \
    NPM_CACHE="/app/.npm" \
    PNPM_HOME="/pnpm" \
    PATH="$PNPM_HOME:$PATH"

RUN --mount=type=cache,target=${APK_CACHE_DIR} \
    mkdir -p ${APK_CACHE_DIR} && \
    ln -fns ${APK_CACHE_DIR} ${APK_SYMLINK_DIR} && \
    apk update && \
    apk add --no-cache libc6-compat

WORKDIR /app

RUN --mount=type=cache,target=${NPM_CACHE} \
    npm install --ignore-scripts -g npm@latest --cache ${NPM_CACHE} && \
    npm install --ignore-scripts -g pnpm --cache ${NPM_CACHE}

COPY --chmod=444 package.json pnpm-lock.yaml ./

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile --ignore-scripts

COPY --chmod=444 .env .pnpmrc next.config.ts postcss.config.js tailwind.config.mjs tsconfig.json ./
COPY --chmod=555 public public
COPY --chmod=555 src src

ARG FORCE_STANDALONE
ENV FORCE_STANDALONE=$FORCE_STANDALONE \
    NEXT_TELEMETRY_DISABLED=1

RUN --mount=type=secret,id=RELEASE_VERSION \
    --mount=type=secret,id=SENTRY_AUTH_TOKEN \
    export NEXT_SENTRY_AUTH_TOKEN=$(cat /run/secrets/SENTRY_AUTH_TOKEN) && \
    export RELEASE_VERSION=$(cat /run/secrets/RELEASE_VERSION) && \
    pnpm run build

# Production image, copy all the files and run next.
FROM base AS runner

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production \
    HOSTNAME="0.0.0.0" \
    PORT=3000

# Fix CVE-2026-23745: Update npm's bundled tar to 7.5.7 and brace-expansion to 5.0.1
# Create user and group in a single RUN layer
RUN cd /tmp && \
    # Download and extract tar 7.5.7
    npm pack tar@7.5.7 && \
    tar -xzf tar-7.5.7.tgz && \
    TAR_DIR="/usr/local/lib/node_modules/npm/node_modules/tar" && \
    rm -rf "${TAR_DIR}" && \
    cp -r package "${TAR_DIR}" && \
    chmod -R 755 "${TAR_DIR}" && \
    rm -rf package tar-7.5.7.tgz && \
    grep -q 'version.*7.5.7' "${TAR_DIR}/package.json" && \
    # Download and extract brace-expansion 5.0.1
    npm pack @isaacs/brace-expansion@5.0.1 && \
    tar -xzf isaacs-brace-expansion-5.0.1.tgz && \
    BRACE_DIR="/usr/local/lib/node_modules/npm/node_modules/@isaacs/brace-expansion" && \
    rm -rf "${BRACE_DIR}" && \
    mkdir -p /usr/local/lib/node_modules/npm/node_modules/@isaacs && \
    cp -r package "${BRACE_DIR}" && \
    chmod -R 755 "${BRACE_DIR}" && \
    rm -rf package isaacs-brace-expansion-5.0.1.tgz && \
    grep -q '"version": "5.0.1"' "${BRACE_DIR}/package.json" && \
    # Create user and group
    addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 -G nodejs nextjs

# Copy application files with appropriate permissions
COPY --from=builder --chown=root:root --chmod=555 /app/public public
COPY --from=builder --chown=root:root --chmod=555 /app/.next/standalone .
COPY --from=builder --chown=root:root --chmod=555 /app/.next/static .next/static

# Create cache directory with proper permissions and remove .env
RUN mkdir -p /app/.next/cache && \
    chown -R nextjs:nodejs /app/.next/cache && \
    chmod -R 755 /app/.next/cache && \
    rm -f .env

USER nextjs

EXPOSE 3000

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/config/next-config-js/output
CMD ["node", "server.js"]
