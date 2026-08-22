FROM mcr.microsoft.com/playwright:v1.62.0-jammy@sha256:b012874f829d298730411256666afcaeaeebaf505a0cf4c2f668d6dedb3d1e80

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
