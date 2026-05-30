FROM mcr.microsoft.com/playwright:v1.59.1-jammy@sha256:8a0360d39d1973be506dd59002904a774f6d697d4946c94063b3fd006461c8ff

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    FORCE_COLOR=1 \
    NPM_CONFIG_CACHE="/app/.npm" \
    PNPM_HOME="/pnpm"

ENV NODE_PATH=/app/e2e/node_modules \
    NPM_CONFIG_RETRY=5 \
    NPM_CONFIG_TIMEOUT=30000 \
    PATH="$PNPM_HOME:$PATH"

WORKDIR /app/e2e

COPY e2e/package.json e2e/pnpm-lock.yaml e2e/pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    corepack install && corepack enable pnpm && \
    pnpm install --frozen-lockfile --ignore-scripts

COPY e2e/ ./
COPY frontend/__tests__/mockData /app/frontend/__tests__/mockData
COPY frontend/src/utils /app/frontend/src/utils

EXPOSE 3800
