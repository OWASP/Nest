# Docker Compose

Committed manifests live under `docker-compose/<stack>/compose.yaml`.

## Volume names on main

Canonical volume names are the top-level `volumes` keys in committed
`docker-compose/*/compose.yaml` files. `.github/scripts/docker_compose_check.py`
derives that allowlist and rejects non-canonical keys, Compose `name:` values,
and service mounts.

The check runs only on GitHub’s `merge_group` event (merge queue), not on
ordinary `pull_request` CI or local pre-commit / `make check`. Temporary custom
names may appear in PR branches for review; merge queue must keep this check
required so they cannot land on `main`.

## Local overrides

Override loading is **local-stack / `make run` only** (`make/run.mk`).
`make run` always passes both:

- `docker-compose/local/compose.yaml`
- `docker-compose/local/compose.override.yaml`

The override file is intentionally empty in-tree (comment-only YAML is stripped
by `yamlfmt`). Put temporary local edits there; revert before merge.

e2e, fuzz, and other stacks use a single `-f` compose file and do not load an
override. Direct `docker compose -f docker-compose/local/compose.yaml …`
commands also skip the override unless you add a second `-f`.

Do not set a top-level Compose `name:` in the override — Docker Compose rejects
it when multiple `-f` files are used. Prefer the Compose project name
(`-p` / `COMPOSE_PROJECT_NAME`) for whole-stack isolation.

Custom volume names are fine on feature branches. Edit the override and set
Compose `name:` on volume keys you need to isolate (keys stay canonical). Merge
queue rejects custom names that are not declared on the base local compose file.

Example:

```yaml
volumes:
  db-data:
    name: db-data-YOUR-SUFFIX
```
