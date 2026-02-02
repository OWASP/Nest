# Badge System

This document explains how user badges work in OWASP Nest, how they are synced,
and what contributors should consider when adding or modifying badges.

Badges are automatically managed by the system. Contributors should not need to
manually assign or update badges in the database.

---

## Overview

Badges represent user roles, achievements, or responsibilities inside the platform.

Examples:
- OWASP Staff
- Project Leaders
- Special contributors
- Future recognition roles

Badges are:
- Stored in the database
- Automatically synced using management commands
- Rendered on the frontend using icons

Each badge contains:

| Field | Purpose |
|-------|---------|
| name | Display name shown in UI |
| description | Optional explanation |
| weight | Controls ordering/priority |
| css_class | Used by frontend to choose the icon |

---

## Architecture

The badge system has two layers that **must always stay in sync**:

### Backend (source of truth)
Location: `apps/nest/models/badge.py`

`BadgeCssClass` enum defines all valid stored values.

Example:

```python
class BadgeCssClass(models.TextChoices):
    AWARD = "award"
    MEDAL = "medal"
    BUG_SLASH = "bugSlash"
```

Only these values should ever be stored in the database.

### Frontend (icon rendering)
Location: `frontend/utils/data.ts`

```typescript
export const BADGE_CLASS_MAP = {
    award: FaAward,
    medal: FaMedal,
    bugSlash: FaBug,
}
```

⚠️ **IMPORTANT**

Backend `css_class` values must exactly match frontend keys.

If they differ:
- Icon not rendered
- Fallback icon used
- Tests may fail

Example:
- ✅ `bugSlash` → works
- ❌ `bug_slash` → icon missing

---

## Badge Sync Flow

Badges are refreshed automatically during GitHub user updates.

Main command:
```bash
python manage.py github_update_users
```

Flow:
1. Fetch users
2. Calculate GitHub contributions
3. Bulk save users
4. Sync badges

After updating users, the command internally calls:
- `nest_update_staff_badges`
- `nest_update_project_leader_badges`

These commands:
- Create badges if missing
- Assign badges to eligible users
- Remove outdated badges
- Keep roles consistent

So badge sync is **automatic** — no manual steps required.

### Where sync happens in code
Location: `apps/github/management/commands/github_update_users.py`

Inside `handle()`:

```python
call_command("nest_update_staff_badges")
call_command("nest_update_project_leader_badges")
```

This guarantees badges stay updated whenever users are refreshed.

---

## Manual Sync (for debugging)

You can run badge updates manually:

```bash
python manage.py nest_update_staff_badges
python manage.py nest_update_project_leader_badges
```

Useful when:
- Testing locally
- Verifying new logic
- Debugging assignments

---

## When are badges updated?

Badges update when:
- `github_update_users` runs
- Sync commands are run manually
- New badge logic is added

---

## Adding a new badge

Steps:
1. Add enum value in `BadgeCssClass`
2. Add icon mapping in frontend `BADGE_CLASS_MAP`
3. Add assignment logic in management command
4. Add tests
5. Run checks

Example:

**Backend:**
```python
NEW_BADGE = "newBadge"
```

**Frontend:**
```typescript
newBadge: FaStar
```

---

## Changing an existing css_class value

If you rename a `css_class`, you **MUST** create a data migration.

Reason: Existing rows already store the old value.

Example: `bug_slash` → `bugSlash`

Migration:
```python
Badge.objects.filter(css_class='bug_slash').update(css_class='bugSlash')
```

Without migration:
- Icons break
- Validation errors
- Inconsistent data

---

## How to verify locally

Run:
```bash
python manage.py github_update_users
```

Expected output:
```
Syncing badges...
Syncing OWASP Staff...
Syncing Project Leaders...
```

Then:
- Check admin panel
- Check UI
- Confirm badges appear

---

## Testing

**Backend:**
```bash
make check-test
```

**Frontend:**
```bash
pnpm test
```

Verify:
- Badges created
- Icons render correctly
- Sync commands execute successfully

---

## Common Issues

### Icon not showing
→ css_class mismatch with frontend map

### Badge not assigned
→ Sync command not executed

### CI failing
→ Missing migration or tests

### Many files modified
→ Run pre-commit

---

## Best Practices

Always:
- Keep backend + frontend keys identical
- Create migration when renaming values
- Add tests
- Run `make check-test`

Never:
- Manually edit DB values
- Rename enums without migration
- Hardcode icons

---

## Mental Model

Think of badges as:

**Database → Sync Commands → Frontend Icons**

If you update one layer, update the others.

---

## Summary

Badges in OWASP Nest are:
- Automatic
- Synced
- Role-based
- Icon-driven

Running `github_update_users` keeps everything consistent.

If something breaks, check: **model → sync → frontend mapping**.
