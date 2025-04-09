FROM node:22-alpine AS base

# Install depencies and build the project
FROM base AS builder
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app

RUN npm install --ignore-scripts -g pnpm 
COPY --chmod=444 package.json pnpm-lock.yaml ./
RUN pnpm install --ignore-scripts

COPY --chmod=444 .env next.config.ts postcss.config.js tailwind.config.js tsconfig.json ./
COPY --chmod=555  public public
COPY --chmod=555 src src

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
# Uncomment the following line in case you want to disable telemetry during runtime.
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
adduser --system --uid 1001 nextjs
# Copying files with root as owner, so that executing user cannot change the container i.e immutable and reproducible
COPY --from=builder --chown=root:root --chmod=555 /app/public public

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/pages/api-reference/config/next-config-js/output
COPY --from=builder --chown=root:root --chmod=555  /app/.next/standalone .
# Create (if not there ) cache directory and assign ownership to nextjs user with write permission, so that cahce can be stored
RUN mkdir -p /app/.next/cache && chown -R nextjs:nodejs /app/.next/cache && chmod -R 755 /app/.next/cache
COPY --from=builder --chown=root:root --chmod=555 /app/.next/static .next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/config/next-config-js/output
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
