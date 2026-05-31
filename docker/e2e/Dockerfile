FROM mcr.microsoft.com/playwright:v1.60.0-jammy@sha256:e1529a04087193966ea15d4a1617345bdaa0791690a24ab2c42b65f9ce5b2cdc

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    FORCE_COLOR=1 \
    NPM_CONFIG_CACHE="/app/.npm" \
    PNPM_HOME="/pnpm"

ENV NODE_PATH=/app/e2e/node_modules \
    PATH="$PNPM_HOME:$PATH" \
    PNPM_CONFIG_FETCH_RETRIES=5 \
    PNPM_CONFIG_FETCH_TIMEOUT=30000

WORKDIR /app/e2e

COPY e2e/package.json e2e/pnpm-lock.yaml e2e/pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    corepack install && corepack enable pnpm && \
    pnpm install --frozen-lockfile

COPY e2e/ ./
COPY frontend/__tests__/mockData /app/frontend/__tests__/mockData
COPY frontend/src/utils /app/frontend/src/utils

EXPOSE 3800
