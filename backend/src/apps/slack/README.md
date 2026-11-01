# NestBot

NestBot handles Slack events, commands and interactivity through Slack Bolt
and Django. The standalone image includes the main and NestBot dependencies;
the regular backend image excludes the NestBot dependencies.

## Local setup

1. Set the bot token and signing secret in `backend/.env`:

   ```dotenv
   DJANGO_SLACK_BOT_TOKEN=xoxb-your-bot-token
   DJANGO_SLACK_SIGNING_SECRET=your-signing-secret
   ```

   Configure the model provider, database and Redis as well. Question detection
   still requires `DJANGO_OPEN_AI_SECRET_KEY`, including with a Google LLM.
   Include the tunnel hostname in `DJANGO_ALLOWED_HOSTS`.

2. Run `make run-nestbot`. Compose starts PostgreSQL, Redis, backend and NestBot,
   waiting for backend migrations. Check `http://127.0.0.1:8003/status/`.
3. Run `ngrok http 8003` using your configured ngrok account.
4. Configure a test Slack app from [MANIFEST.yaml](MANIFEST.yaml), replacing
   **every** command, event and interactivity URL host with your HTTPS tunnel
   host. Preserve the default features and scopes; verify the event URL and
   reinstall if Slack requests it. [MANIFEST.local.yaml](MANIFEST.local.yaml)
   is optional for a new mention-only test app.
5. Invite the bot and enable your channel using its workspace and channel IDs:

   ```bash
   docker compose -f docker-compose/local/compose.yaml exec nestbot \
     python manage.py slack_enable_assistant \
     --workspace-id T0123456789 --channel-id C0123456789
   ```

Mention the bot with an OWASP question. Confirm one answer in the same thread
and no answer in a disabled channel. Useful answers require indexed RAG data.
Inspect failures with `docker compose -f docker-compose/local/compose.yaml logs --tail=100 nestbot`.

## Staging

Use a separate staging Slack app configured from the full default manifest.
Replace every `nest.owasp.org` URL host with `nest.owasp.dev`, retaining paths,
features and scopes. Keep the committed production manifest unchanged.

Slack sends HTTPS requests to the existing ALB, which routes
`/integrations/slack/*` to NestBot after cutover. No tunnel or running laptop is
needed. Store the staging app's token/signing secret in staging SSM, verify the
Events URL in Slack, invite the bot and enable the staging workspace/channel.
Test a mention, `/ai`, an existing command and interactivity after cutover.

Mentions and `/ai` run through the web service. The default manifest also enables
ordinary channel messages; delayed automatic replies require an `ai` RQ worker
with scheduling. That worker is **not yet provisioned by staging Terraform**.
For a focused mention test, temporarily unsubscribe `message.channels` in the
test app. Keep this as an explicit rollout gap before claiming full app support.

## Image

Build from the repository root:

```bash
docker build -f docker/backend/Dockerfile.nestbot -t nestbot:local backend
```

The image runs Gunicorn as a non-root user on port 8000. Supply staging Django,
SSM/provider and database/cache configuration at runtime. Run migrations before
starting services; startup only starts Gunicorn. Health checks must GET
`/status/` because the Django endpoint rejects HEAD.

Deployment order and Terraform settings are in the
[infrastructure README](../../../../infrastructure/live/README.md#nestbot-staging).
