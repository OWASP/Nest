FROM node:22-alpine AS builder

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install --ignore-scripts -g pnpm && \
    pnpm install --ignore-scripts
COPY . .

RUN pnpm run build

FROM builder AS production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD pnpm run start