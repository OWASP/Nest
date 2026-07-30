# Maintenance

This section documents maintenance procedures for OWASP Nest, including dependency
updates, vulnerability scanning, and security.txt renewal.

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

## security.txt renewal

Nest publishes RFC 9116 disclosure metadata at
[`frontend/public/.well-known/security.txt`](https://github.com/OWASP/Nest/blob/main/frontend/public/.well-known/security.txt)
and an OpenPGP public key at
[`frontend/public/.well-known/pgp-key.txt`](https://github.com/OWASP/Nest/blob/main/frontend/public/.well-known/pgp-key.txt).

Renew when `Expires` is within about 30 days (tools tests warn) or when rotating
the Nest security mailbox key. GnuPG runs inside
`docker/tools/Dockerfile.security` — no host `gpg` install is required.

### Renew

Provide a PGP passphrase via `NEST_SECURITY_PGP_PASSPHRASE` (avoid putting
passphrases on the CLI / shell history):

```bash
export NEST_SECURITY_PGP_PASSPHRASE='...'
make tools-renew-security-txt
```

Pass extra flags with `RENEW_SECURITY_TXT_ARGS`:

```bash
make tools-renew-security-txt \
  RENEW_SECURITY_TXT_ARGS='--expires 2028-07-01T00:00:00-07:00'
```

That builds/runs the Nest security image, which executes
[`tools/security/renew_security_txt.py`](https://github.com/OWASP/Nest/blob/main/tools/security/renew_security_txt.py)
and:

1. Generates a passphrase-protected Ed25519 OpenPGP key for
   `OWASP Nest Security <nest+security@owasp.org>` whose GnuPG expiry matches
   `security.txt` `Expires`
2. Clearsigns `security.txt` with that key (RFC 9116 §2.3). Any existing
   clearsign wrapper is stripped first so the file is never double-signed.
3. Writes the public key to `frontend/public/.well-known/pgp-key.txt`
4. Writes the clearsigned `frontend/public/.well-known/security.txt`
5. Exports the private key to `tools/security/private/`

### After renewing

1. Store the private key **and passphrase** in the organization secret store used
   for Nest security mail, then delete the local export under
   `tools/security/private/`.
2. Never commit private key material or passphrases.
3. Open a PR with the updated `security.txt` and `pgp-key.txt`.
4. After deploy, confirm
   `https://nest.owasp.org/.well-known/security.txt` and
   `https://nest.owasp.org/.well-known/pgp-key.txt` resolve. Playwright e2e
   also covers serving these paths against the Nest frontend (`WellKnown.spec.ts`).
5. Run `make test-tools` (or `make check-test-tools`) so the security.txt checks
   stay green.
