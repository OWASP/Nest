# NestBot Maintainer Guide

## 1. Enable the bot on a new channel

1. Django Admin → **Slack → Conversations**
2. Search for the channel
3. Tick **Is Nest Bot Assistant Enabled** → Save

Or bulk action: Select conversations → **"Enable NestBot assistant"** → Go

**Rollback:** Untick `is_nest_bot_assistant_enabled` — bot goes silent immediately, no deploy needed.

## 2. Edit the system prompt without a deploy

1. Django Admin → **Core → Prompts**
2. Find key `nestbot-slack-system-prompt`
3. Edit **Text** → Save — takes effect on next message

If the key doesn't exist yet, create it via Add Prompt with key `nestbot-slack-system-prompt`.

## 3. Monitoring queries

```python
# Thumbs-up rate (last 7 days)
from django.utils import timezone
from apps.slack.models.bot_interaction import BotInteraction
qs = BotInteraction.objects.filter(nest_created_at__gte=timezone.now() - timezone.timedelta(days=7), thumbs_up__isnull=False)
total = qs.count()
positive = qs.filter(thumbs_up=True).count()
print(f"{positive}/{total} = {positive/total*100:.1f}% positive" if total else "No feedback")

# Redirect rate
from django.db.models import Count
BotInteraction.objects.exclude(intent_category="general_owasp").values("intent_category").annotate(count=Count("id")).order_by("-count")
```

## 4. Staged rollout order

```
1. #project-nest-bot-testing  ← internal UAT
2. OWASP project channels     ← #project-nest, #project-juiceshop, etc.
3. #owasp-community           ← announce to community
```
