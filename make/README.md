# Root Make Targets

The root `make/` directory contains repository-wide targets. These targets usually
coordinate the backend, frontend, and other project components.

## Naming

Use short, unprefixed names for high-level operations:

- `check`
- `check-fix`
- `clean`
- `run`
- `security-scan`
- `test`

Use a descriptive suffix only when a repository-wide operation has meaningful
variants, such as `security-sast-scan`, `security-filesystem-scan`,
`security-dast-scan`, and `security-image-scan`.

Do not add `backend-` or `frontend-` prefixes here. Component-specific targets
belong in their component's `make/` directory.

## Files

Use one singular, goal-based filename for each target group:

- `check.mk`
- `check-test.mk`
- `help.mk`
- `maintenance.mk`
- `run.mk`
- `security.mk`
- `shell.mk`
- `terraform.mk`
- `test.mk`

Keep the root `Makefile` as a thin aggregator that includes these files.

## Help

Only high-level repository targets should appear in `make help`. Add a `##`
description to public high-level targets and omit it from internal helpers,
and component-specific implementation targets. When a public compatibility
alias exists, put the description on the alias instead of its replacement.

The help command scans the root orchestration files listed in `HELP_MAKEFILES`,
plus the component files that define public `test-*` and maintenance targets so
they appear under `Code tests` and `Maintenance`. It does not display other
backend, frontend, or infrastructure targets. Targets within each help section
are sorted alphabetically.
