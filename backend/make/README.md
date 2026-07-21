# Backend Make Targets

The backend `make/` directory contains shared backend targets and app-specific
operations.

## Shared Target Naming

Name shared targets using:

```text
backend-<group>-<action>
```

Use a singular group name that matches the owning file:

- `backend-clean-dependencies`
- `backend-data-load`
- `backend-dependency-compile-requirements`
- `backend-django-migrate`
- `backend-exec-shell`
- `backend-image-build`
- `backend-security-image-scan`
- `backend-test-fuzz`

The group-level target may omit the action, as in `backend-test`.

## App Target Naming

Targets in `apps/` are already scoped by their app and do not use the
`backend-` prefix:

```text
<app>-<action>
```

Examples include `github-update-users`, `owasp-enrich-projects`, and
`slack-sync-data`.

## Files

Use singular, goal-based filenames such as `maintenance.mk`, `image.mk`, and
`test.mk`. Keep `backend/Makefile` as a thin aggregator that includes shared and
app-specific files. Backend test tooling is included through `test.mk`;
`test.mk` includes `clusterfuzz.mk`.

## Compatibility

Place backward-compatible aliases in the same file as the replacement target.
For example, `migrate` delegates to `backend-django-migrate`.

The compatibility alias is the public interface: if it has a `##` help
description, put it on `migrate`, not on `backend-django-migrate`. Root
`make help` displays only repository-wide targets and filters out backend
targets. Prefer a repository-wide aggregator when one exists, such as
`security-dependency-audit` instead of component-level audit aliases.

List compatibility aliases at the top of the file. Add an
`# Implementation targets.` comment before variables and replacement targets.
