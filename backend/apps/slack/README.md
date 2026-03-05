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
