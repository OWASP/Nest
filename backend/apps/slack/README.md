# Nestbot Overview

Nestbot is the custom Slack integration for the OWASP Nest project, built using the [Slack Bolt for Python](https://docs.slack.dev/tools/bolt-python/getting-started) framework within Django.

## Tech Stack

| Component         | Technology                         |
| ----------------- | ---------------------------------- |
| **Framework**     | Slack Bolt (Python)                |
| **Integration**   | Django (as a standard app)         |
| **Hosting**       | AWS Lambda (via Zappa)             |

## Directory Structure

The Nestbot code lives in `backend/apps/slack/`. Key directories include:

- `commands/` - Handlers for Slack slash commands (e.g., `/nest`).
- `events/` - Handlers for Slack events (e.g., when a user joins a channel).
- `actions/` - Handlers for interactive components (e.g., button clicks).
- `models/` - Django models for storing Slack workspaces, messages, and users.
- `templates/` - Slack Block Kit JSON templates for rich messages.

## Key Commands

The project provides `Makefile` targets to manage Slack data:

| Task                             | Command                                            |
| -------------------------------- | -------------------------------------------------- |
| Sync Slack workspace data        | `make slack-sync-data`                             |
| Sync recent Slack messages       | `make slack-sync-messages`                         |
| Export Slack data to JSON        | `make slack-export-data`                           |
