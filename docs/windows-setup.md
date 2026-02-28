# Windows Contributor Setup Guide

This guide provides a dedicated onboarding path for contributors using Windows.

!!! info "Recommended Approach"
    Nest is designed to run from a Linux environment. On Windows, the supported workflow is **WSL2 + Docker Desktop + a WSL terminal**.

## 1) Install prerequisites

### Required software

1. **Git for Windows**
    - Download: [https://git-scm.com/download/win](https://git-scm.com/download/win)
    - During installation, keep defaults unless your organization requires specific settings.

2. **Docker Desktop**
    - Download: [https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)
    - Docker Desktop must be configured to use **WSL2**.

3. **WSL2 (Windows Subsystem for Linux)**
    - Install from an elevated PowerShell:

      ```powershell
      wsl --install
      ```

    - Restart Windows if prompted.
    - Install or open Ubuntu (or another supported Linux distro).

4. **Python + pre-commit inside WSL**
    - In your WSL terminal:

      ```bash
      sudo apt update
      sudo apt install -y python3 python3-pip python3-venv make
      pip3 install --user pre-commit
      ```

5. **Node.js (optional for direct frontend tooling)**
    - Most project commands run in Docker, but local Node.js can still be useful.
    - In WSL, install Node.js LTS using your preferred manager (for example `nvm`).

## 2) Configure Docker + WSL correctly

1. Open Docker Desktop.
2. Navigate to **Settings → Resources → WSL Integration**.
3. Enable integration for your Linux distro.
4. Verify Docker works from WSL:

```bash
docker version
docker compose version
```

!!! danger "Run commands from WSL, not PowerShell"
    Use a WSL terminal for Nest commands. Running `make run`, tests, and linting from PowerShell is not supported.

## 3) Clone and place the repository in WSL filesystem

From your WSL terminal:

```bash
cd ~
git clone https://github.com/<your-account>/Nest.git
cd Nest
```

!!! warning "Avoid `/mnt/c` for this project"
    Do not develop inside `/mnt/c/...` (Windows filesystem mount). It can cause slower I/O and Docker permission/path issues.

## 4) Initialize local environment files

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Update backend environment mode:

```bash
printf '\nDJANGO_CONFIGURATION=Local\n' >> backend/.env
```

If needed, configure Algolia credentials as described in the main contributing guide.

## 5) Start the project

```bash
make run
```

In another terminal:

```bash
make load-data
make index-data
```

Verify local endpoints:

- [http://localhost:8000/api/v0/projects/](http://localhost:8000/api/v0/projects/)
- [http://localhost:8000/api/v0/issues/](http://localhost:8000/api/v0/issues/)

## 6) Run linting and tests on Windows (via WSL)

Run these from the repository root in WSL:

```bash
make check
make test
```

You can also run focused checks:

```bash
make check-backend
make check-frontend
make test-backend
make test-frontend
```

## 7) Troubleshooting common Windows issues

### Docker permission or connectivity errors

**Symptoms**
- `Cannot connect to the Docker daemon...`
- `permission denied` while running Docker commands.

**Fixes**
- Ensure Docker Desktop is started.
- Re-check Docker Desktop → WSL integration.
- Restart Docker Desktop and your WSL distro:

  ```powershell
  wsl --shutdown
  ```

  Then reopen WSL and retry.

### Path translation and volume mount issues

**Symptoms**
- Files not syncing as expected in containers.
- Build or startup scripts failing with path errors.

**Fixes**
- Confirm repository path is under Linux home (for example `~/Nest`), not `/mnt/c/...`.
- Avoid mixing Windows tools/editors that rewrite line endings unexpectedly.

### Dependency installation failures

**Symptoms**
- Python package install errors.
- Node package post-install failures.

**Fixes**
- Rebuild containers and dependencies:

  ```bash
  make clean
  make run
  ```

- Check free disk space in Docker Desktop.
- Ensure your network/proxy settings allow package registries.

### Environment variable issues

**Symptoms**
- Missing-key errors during startup.
- Unexpected configuration mode.

**Fixes**
- Confirm both files exist and were copied from examples:
  - `backend/.env`
  - `frontend/.env`
- Ensure `.env` files are UTF-8 without BOM.
- Re-run containers after `.env` updates:

  ```bash
  make run
  ```

### Port conflicts on Windows

**Symptoms**
- Errors indicating a port is already in use.

**Fixes**
- Close local services using the same ports.
- If needed, identify processes from WSL:

  ```bash
  ss -ltnp
  ```


## If any error appears while you are setting up

Use this quick sequence before deep troubleshooting:

1. Confirm you are inside WSL (not PowerShell):

   ```bash
   uname -a
   pwd
   ```

2. Confirm Docker is reachable from WSL:

   ```bash
   docker version
   docker compose version
   ```

3. Confirm you are in a Linux path (recommended: `~/Nest`, not `/mnt/c/...`).
4. Re-check env files exist and are populated from examples:

   ```bash
   ls -la backend/.env frontend/.env
   ```

5. Retry with a clean restart:

   ```powershell
   wsl --shutdown
   ```

   Then reopen WSL and run:

   ```bash
   make clean
   make run
   ```

If the issue persists, capture the exact command and full error output, then open a discussion/issue with those logs and your Windows + WSL + Docker versions.

## 8) Contribution workflow tips for Windows users

- Keep your terminal in WSL for all Nest commands.
- Run `pre-commit run -a` before opening a PR.
- Run `make check` and `make test` before pushing.
- If you use VS Code, use the **Remote - WSL** extension so editing and terminal execution stay in the same Linux environment.

## Related docs

- [Main Contributing Guide](contributing.md)
- [Documentation Home](index.md)
