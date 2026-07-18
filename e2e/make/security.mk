.PHONY: e2e-dependency-audit

e2e-dependency-audit:
	@echo "Auditing e2e npm dependencies..."
	@docker run \
		--rm \
		-e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
		-v "$(CURDIR)/e2e:/work" \
		-w /work \
		--mount type=volume,dst=/work/node_modules \
		$$(grep -E '^FROM node:' docker/code-checks/Dockerfile | sed 's/^FROM //; s/ AS .*//' | head -1) \
		sh -c 'corepack enable && \
		corepack prepare pnpm@11.7.0 --activate && \
		pnpm install --frozen-lockfile && \
		pnpm audit --audit-level=high'
