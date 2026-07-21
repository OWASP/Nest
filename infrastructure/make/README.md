# Infrastructure Make Targets

The infrastructure `make/` directory contains Terraform tooling targets. Every
target runs inside Docker so no host Terraform, Poetry, or Python is required.

## Shared Target Naming

Name shared targets using:

```text
infrastructure-<group>-<action>
```

Use a singular group name that matches the owning file:

- `infrastructure-clean-docker`
- `infrastructure-dependency-audit`
- `infrastructure-test-integration`
- `infrastructure-test-unit`

The group-level target may omit the action, as in `infrastructure-test`.

## Files

Use singular, goal-based filenames such as `maintenance.mk`, `security.mk`, and
`test.mk`. Keep `infrastructure/Makefile` as a thin aggregator that includes
these files.

## Compatibility

Place backward-compatible aliases in the same file as the replacement target.
The public `test-infrastructure`, `test-infrastructure-unit`, and
`test-infrastructure-integration` aliases live in `test.mk` and delegate to
their `infrastructure-test*` implementations; the `##` help description sits on
the alias. Prefer the repository-wide aggregator when one exists, such as
`security-dependency-audit` instead of a component-level audit alias.
