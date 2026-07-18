# Frontend Make Targets

The frontend `make/` directory contains targets specific to the frontend.

## Naming

Name targets using:

```text
frontend-<group>-<action>
```

Use a singular group name that matches the owning file:

- `frontend-clean-dependencies`
- `frontend-dependency-audit`
- `frontend-exec-shell`
- `frontend-image-build`
- `frontend-security-image-scan`
- `frontend-test-unit`

The group-level target may omit the action, as in `frontend-test`.

## Files

Use singular, goal-based filenames such as `image.mk`, `security.mk`, and
`test.mk`. Keep `frontend/Makefile` as a thin aggregator that includes them.

## Compatibility

Place backward-compatible aliases in the same file as the replacement target.
For example, `test-frontend` delegates to `frontend-test`.

The compatibility alias is the public interface: if it has a `##` help
description, put it on `test-frontend`, not on `frontend-test`. Root
`make help` displays only repository-wide targets and filters out frontend
targets. Prefer a repository-wide aggregator when one exists, such as
`security-dependency-audit` instead of component-level audit aliases.

List compatibility aliases at the top of the file. Add an
`# Implementation targets.` comment before variables and replacement targets.
