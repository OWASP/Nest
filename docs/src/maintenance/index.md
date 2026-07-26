# Maintenance

This section documents maintenance procedures for OWASP Nest, including dependency
updates and vulnerability scanning.

## Dependency maintenance

Nest keeps dependencies current through Dependabot version updates and
security-driven fixes when audits or scans find actionable vulnerabilities.
Prefer fixes that have an available patched release.

Configuration lives in [`.github/dependabot.yml`](https://github.com/OWASP/Nest/blob/main/.github/dependabot.yml).

### Dependabot version updates

Dependabot opens daily, grouped version-update PRs on `main` for:

- docker
- docker-compose
- github-actions
- pnpm (Dependabot ecosystem `npm`)
- poetry (Dependabot ecosystem `pip`)
- pre-commit
- terraform

Each ecosystem uses a 21-day cooldown so routine bumps wait for mature releases.
Review the PR, ensure CI is green, then merge.

Docker updates ignore major bumps for `node`, and major/minor bumps for
`python`, as configured in Dependabot.

### Detect vulnerabilities

For dependency findings, run:

```bash
make security-dependency-scan
```

That target runs package-manager audits (Poetry / pnpm), OSV, and Trivy
vulnerability scanning. When the finding is in a container image (including
Node/npm-bundled packages), also run:

```bash
make security-image-scan
```

Also watch Dependabot pull requests and GitHub dependency alerts.

### Unfixed findings

Trivy ignores vulnerabilities with no available fix
(`vulnerability.ignore-unfixed: true` in
[`.trivy.yaml`](https://github.com/OWASP/Nest/blob/main/.trivy.yaml)).

OSV (part of `security-dependency-scan`) and `pnpm audit` may still report
unfixed findings. Treat those as advisory unless a fix exists — do not open
empty PRs for CVEs with no patched release. Accepted Trivy findings can be
recorded in
[`.trivyignore.yaml`](https://github.com/OWASP/Nest/blob/main/.trivyignore.yaml).

### Security updates

When a finding needs a fix sooner than cooldown or age gates allow, update
dependencies manually (or merge a Dependabot security PR) using the path for
that ecosystem.

#### pnpm

pnpm workspaces enforce a 21-day `minimumReleaseAge` in each
`pnpm-workspace.yaml` (root, `frontend/`, `e2e/`, `cspell/`). Edit the workspace
that owns the vulnerable package (and its lockfile).

**Project and transitive packages:** bump the direct dependency when possible,
or pin the patched version with `overrides` in that workspace’s
`pnpm-workspace.yaml`. If the release is younger than 21 days, also add the
exact `package@version` to `minimumReleaseAgeExclude` (security pins usually
need both). Refresh the lockfile, then re-run `make security-dependency-scan`.

**Node/npm-bundled packages:** vulnerabilities inside the Node image’s bundled
npm tree (under `/usr/local/lib/node_modules/npm/...`) are **not** fixed with
pnpm overrides. Patch them in the Dockerfile by packing the fixed package and
replacing the bundled copy, with CVE comments — see
[`docker/frontend/Dockerfile`](https://github.com/OWASP/Nest/blob/main/docker/frontend/Dockerfile).
Validate with `make security-image-scan`.

#### poetry

Poetry enforces `min-release-age = 21` in
[`backend/poetry.toml`](https://github.com/OWASP/Nest/blob/main/backend/poetry.toml),
[`docs/poetry.toml`](https://github.com/OWASP/Nest/blob/main/docs/poetry.toml),
and
[`infrastructure/poetry.toml`](https://github.com/OWASP/Nest/blob/main/infrastructure/poetry.toml).
Bump the package and refresh the lockfile. If the release is newer than 21 days,
add the package **name** (not `name@version`) to `min-release-age-exclude` in
the matching `poetry.toml`. Dependabot covers `backend` and `docs` only;
infrastructure Poetry updates are manual.

#### Other ecosystems

For github-actions, pre-commit, docker, docker-compose, and terraform, prefer
Dependabot PRs. When a security fix cannot wait, bump the pin or image tag
manually in the same files Dependabot would change.

### Verify

After applying a fix:

1. Re-run the Detect commands above (`make security-dependency-scan`, and
   `make security-image-scan` when relevant).
2. Confirm CI **Dependency audit** and **Dependency scan** jobs no longer
   report the finding.
3. Once a release is older than 21 days and the lockfile still resolves without
   them, remove obsolete `minimumReleaseAgeExclude` /
   `min-release-age-exclude` entries.
