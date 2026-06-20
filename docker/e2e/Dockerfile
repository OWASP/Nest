FROM mcr.microsoft.com/playwright:v1.61.0-jammy@sha256:264136758e43332108f6420f82c47f639f619ca65301065ceade677763f477ec

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
