# NestBot

NestBot is the custom Slack integration for the OWASP Nest project, built using the [Slack Bolt for Python](https://docs.slack.dev/tools/bolt-python/getting-started) framework within Django.

## Tech Stack

| Component         | Technology                         |
| ----------------- | ---------------------------------- |
| **Frameworks**    | Slack Bolt, Slack SDK (Python)     |
| **Integration**   | Django (as a standard app)         |

## Directory Structure

- `actions/`   - Handlers for interactive components (e.g., button clicks).
- `commands/`  - Handlers for Slack slash commands (e.g., `/nest`).
- `events/`    - Handlers for Slack events (e.g., when a user joins a channel).
- `models/`    - Django models for storing Slack workspaces, messages, and users.
- `templates/` - Slack Block Kit JSON templates for rich messages.

## Local Slack demo

The existing NestBot container serves Slack requests on port **8001**.
It shares PostgreSQL and Redis with the backend. The website frontend and
background worker are not needed for explicit mentions.

### 1. Configure the test app

Create a Slack app in your test workspace. Add these bot token scopes under
**OAuth & Permissions**, then install the app:

- `app_mentions:read`
- `chat:write`
- `reactions:write`

Put its bot token and signing secret in `backend/.env`:

```dotenv
DJANGO_SLACK_BOT_TOKEN=xoxb-your-test-bot-token
DJANGO_SLACK_SIGNING_SECRET=your-test-signing-secret
```

Keep your working LLM provider/model settings and credentials in that file too.
Use the same provider for embeddings unless you have configured another one.
Compose selects local Django settings and supplies the database/cache addresses.
Set `DJANGO_ALLOWED_HOSTS` to include `127.0.0.1`, `localhost`, and your tunnel
hostname; `*` also works for local development.

### 2. Start NestBot

From the repository root:

```bash
make run-nestbot
```

This builds and starts the backend and NestBot with PostgreSQL and Redis.
NestBot waits for the backend to finish migrations and become healthy.

Verify the NestBot server locally:

```bash
curl --fail http://127.0.0.1:8001/status/
```

### 3. Enable your test channel

Use your actual workspace ID (`T...`) and channel ID (`C...`):

```bash
docker compose -f docker-compose/local/compose.yaml exec nestbot \
  python manage.py slack_enable_assistant \
  --workspace-id T0123456789 --channel-id C0123456789
```

The command creates missing records and enables only that channel. Repeating it
keeps existing channel settings. A channel in another workspace is rejected.
The IDs are supplied by you; this command does not validate them with Slack.

### 4. Connect Slack through ngrok

For Linux x86_64, install the standalone binary without sudo:

```bash
mkdir -p ~/.local/bin
curl -fsSL https://bin.ngrok.com/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz \
  -o /tmp/ngrok.tgz
tar -xzf /tmp/ngrok.tgz -C ~/.local/bin ngrok
```

Sign in to your [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
and copy your authtoken. Configure it locally and start the tunnel:

```bash
~/.local/bin/ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
~/.local/bin/ngrok http 8001
```

The ngrok authtoken connects the tunnel to your ngrok account. It is separate
from the Slack bot token and signing secret. It does not go in the manifest.
See [ngrok's Linux installation instructions](https://ngrok.com/download/linux)
for other installation methods.

For a new mention-only test app, copy `MANIFEST.local.yaml`, replace
`https://replace-me.ngrok-free.app` with your HTTPS forwarding URL, and paste it
into **App Manifest**. This template does not enable slash commands, ordinary
channel messages, or direct messages.

For an existing full app, keep its manifest and replace the host in its event,
slash-command, and interactivity URLs. Keep their paths and existing features.
For the mention-only demo, unsubscribe from `message.channels` until a background
worker is available for automatic replies.

Save and reinstall if Slack requests it. Under **Event Subscriptions**, check
that the request URL is verified. Invite the bot to your test channel. Update
the URLs whenever your tunnel address changes.

### 5. Test the conversation

Mention your bot (`@NestBot Local` for the template) with an OWASP question.
Expect an eyes reaction and one
answer in the question's thread. Mention it inside that thread and confirm the
next answer stays there. Mobile notifications should contain the answer.

Also check that an unconfigured channel gets no answer and an ordinary message
without a mention gets no automatic reply. An error/fallback message does not
establish that the agent is working. Useful retrieval answers require OWASP
records and indexed documents in the local database.

Inspect failures with:

```bash
docker compose -f docker-compose/local/compose.yaml logs --tail=100 backend nestbot
```

Keep the containers and ngrok running during the demo. For staging, replace the
tunnel with permanent HTTPS routing to a deployed NestBot service; the local
Compose setup does not deploy staging.

## Standalone NestBot image

Build from the repository root:

```bash
docker build -f docker/backend/Dockerfile.nestbot -t nestbot:local backend
```

This image includes the application, templates, and locked main/NestBot Python
dependencies. It runs as a non-root user and starts Gunicorn on port 8000.
Application files and a host virtual environment do not need to be mounted.

Supply environment variables at runtime using an environment file locally or
the deployment's secret configuration. For a local smoke test with staging
settings, use your configured environment file and an unused host port:

```bash
docker run --rm --name nestbot-package --env-file backend/.env \
  -e DJANGO_SETTINGS_MODULE=settings.staging -e DJANGO_CONFIGURATION=Staging \
  -p 127.0.0.1:8003:8000 nestbot:local
```

The configuration must include the allowed hosts, staging static bucket name,
Sentry DSN, database/Redis connection details, Slack credentials, and model credentials.
Container database/cache addresses must resolve on its Docker network; attach
the appropriate network when using other local containers. Check `/status/` on
the published port after startup. The image health check uses an HTTP GET to
`/status/`; the ECS task definition must also use GET. GNU `wget --spider` sends
HEAD, which this endpoint rejects.

Startup only runs the web server. Run database migrations separately before
serving application traffic. OWASP documents, chunks, and embeddings remain in
PostgreSQL and must be populated separately; the image does not include a RAG
dataset. Terraform service/routing and CI publishing are separate staging tasks.
