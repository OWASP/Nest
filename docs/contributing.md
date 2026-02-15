# Contributing to Nest

!!! note "Thank You"
    Thank you for considering contributing to the **OWASP Nest** project! This document provides guidelines to help you get started.

## Project Overview

Nest is a full-stack web application built using:

- **Backend**: Python, Django
- **Frontend**: TypeScript, React, Tailwind CSS
- **Search**: Algolia

!!! info "Containerization"
    The project uses a **containerized approach** for both development and production environments. Docker is required to run Nest locally.

## Prerequisites

Before contributing, ensure you have the following installed:

### Required Tools

1. **Docker**
    - Required for running the Nest instance
    - [Docker Documentation](https://docs.docker.com/)

2. **pre-commit**
    - Required to automate code checks and apply fixes
    - Installation options:
        - Virtual environment: `pip install pre-commit`
        - OS package: `apt install pre-commit` / `brew install pre-commit`
        - Other methods depending on your configuration

### Windows Users Requirements

!!! warning "Windows Setup Requirements"
    **WSL (Windows Subsystem for Linux)** is required for Windows users to enable Linux compatibility.

```plaintext
1. The `make run` command requires WSL
2. You must use WSL terminal (not Windows PowerShell)
3. WSL integration must be enabled in Docker Desktop settings

=== "WSL Installation"
    Follow [Microsoft's official guide](https://learn.microsoft.com/en-us/windows/wsl/install)

=== "Docker Desktop Setup"
    1. Open Docker Desktop
    2. Go to Settings → Resources → WSL Integration
    3. Enable WSL integration

!!! danger "PowerShell Not Supported"
    Do not report issues if using PowerShell for running commands -- it's not the intended way to run Nest locally.
```

## Getting Started

### Support the Project

- [![GitHub stars](https://img.shields.io/github/stars/OWASP/Nest?style=social)](https://github.com/OWASP/Nest)

- [![GitHub forks](https://img.shields.io/github/forks/OWASP/Nest?style=social)](https://github.com/OWASP/Nest/fork)

### Initial Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/<your-account>/<nest-fork>
    ```

2. **Environment Setup**

    === "Backend Environment"
        ```bash
        touch backend/.env
        ```
        **Copy the contents from the template file into your new local environment file:**
        ```bash
        cat backend/.env.example > backend/.env
        ```

    === "Frontend Environment"
        ```bash
        touch frontend/.env
        ```
        **Copy the contents from the template file into your new local environment file:**
        ```bash
        cat backend/.env.example > frontend/.env
        ```

    !!! warning "File Encoding"
        Ensure all `.env` files are saved in **UTF-8 format without BOM (Byte Order Mark)** to prevent "Unexpected character" errors.

    !!! note "Environment Changes"
        Restart the application to apply any `.env` file changes.

3. **Configure Environment**

    Update `backend/.env`:

    ```plaintext
    DJANGO_CONFIGURATION=Local
    ```

4. **Algolia Setup**

    1. Create a free [Algolia](https://www.algolia.com/) account
    2. Create an Algolia app
    3. Configure environment files:

    === "Backend Configuration"
        Update `backend/.env` with write API key:
        ```plaintext
        DJANGO_ALGOLIA_APPLICATION_ID=<your-algolia-application-id>
        DJANGO_ALGOLIA_WRITE_API_KEY=<your-algolia-write-api-key>
        DJANGO_ALGOLIA_APPLICATION_REGION=<your-algolia-application-region> // eu or us
        ```

    === "Frontend Configuration"
        Update `frontend/.env` with search API key:
        ```plaintext
        VITE_ALGOLIA_APP_ID=<your-algolia-application-id>
        VITE_ALGOLIA_SEARCH_API_KEY=<your-algolia-search-api-key>
        ```

5. **Run the Application**

    ```bash
    make run
    ```

    !!! note
        *Run this from the project root directory
        * Keep this terminal session running
        *Wait for [Nest local](http://localhost:8000/api/v0) to respond
        * Use separate terminal sessions for other commands

6. **Initialize Data**

    ```bash
    make load-data
    make index-data
    ```

7. **Verify Setup**

    Check these endpoints:
    <br>
    > [Projects Endpoint](http://localhost:8000/api/v0/projects/)
    <br>
    > [Issues Endpoint](http://localhost:8000/api/v0/issues/)

## Optional Setup

### GitHub Data Integration

To fetch GitHub OWASP data locally:

1. **Create Super User**

    ```bash
    make create-superuser
    ```

2. **Configure GitHub Access**
    1. Create a [GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
    2. Add to `backend/.env`:

        ```plaintext
        GITHUB_TOKEN=<your-github-token>
        ```

3. **Sync Data**

    ```bash
    make sync-data
    ```

### NestBot Development

!!! danger "Important Notice"
    Never install your development Slack application in the OWASP Slack workspace.
    This will interfere with OWASP Nest functionality and trigger unnecessary notifications.
    Always use a different workspace (create your own if needed).

1. **ngrok Setup**
    1. Create [ngrok](https://ngrok.com/) account
    2. Follow [installation instructions](https://ngrok.com/docs/getting-started/#step-1-install)
    3. Create static domain at [ngrok domains](https://dashboard.ngrok.com/domains)
    4. Configure ngrok:

        ```bash
        ngrok config edit
        ```

        ```yaml
        agent:
            authtoken: <your-auth-token>
        tunnels:
            NestBot:
              addr: 8000
              proto: http
              hostname: <your-static-domain>
        ```

    5. Start ngrok:

        ```bash
        ngrok start NestBot
        ```

2. **Update NestBot Configuration**

    Add to `backend/.env`:

    ```plaintext
    DJANGO_SLACK_BOT_TOKEN=<your-slack-bot-token>
    DJANGO_SLACK_SIGNING_SECRET=<your-slack-signing-secret>
    ```

3. **Configure Slack App**
    - Use [NestBot manifest file](https://github.com/OWASP/Nest/blob/main/backend/apps/slack/MANIFEST.yaml) (copy its contents and save it into `Features -- App Manifest`).
    - Replace slash commands endpoint with your ngrok domain
    - Reinstall your Slack application after making the changes using `Settings -- Install App` section

## Development Guidelines

### Code Quality

```bash
make check
#This command runs linters and other static analysis tools for both the frontend and backend.
```

!!! warning
    PRs failing code quality checks will not be reviewed.

### Testing

```bash
make test
#Our CI/CD pipelines automatically run tests against every Pull Request,
#You can run tests locally before submitting a PR.
```

!!! warning
    PRs failing tests will not be merged.

#### Test Coverage

- Minimum test coverage requirement for the Backend: [pyproject.toml](https://github.com/OWASP/Nest/blob/main/backend/pyproject.toml)
- Minimum test coverage requirement for the Frontend: [jest.config.ts](https://github.com/OWASP/Nest/blob/main/frontend/jest.config.ts)

!!! danger "Important Notice"
    - Ensure your changes do not drop the overall test coverage percentage.
    - If you are adding new functionality, include relevant test cases.

## Contributing Process

### 1. Find an Issue

- Browse [issues](https://github.com/owasp/nest/issues)
- If you want to work on something specific, create a new issue or comment on an existing one to let others know

### 2. Branch Creation

```bash
git checkout -b feature/my-feature-name
#Always create a feature branch for your work
```

### 3. Make Changes and Commit

- Check that your commits include only related and intended changes. Do not include unrelated files.
- Follow best practices for code style and testing.

- **Add tests** for any new functionality or changes to ensure proper coverage.
  - **Run the code quality checks**:

      ```bash
      make check
      ```

  - **Run tests to ensure everything works correctly**:

      ```bash
      make test
      ```

  - **Write meaningful commit messages**:

      ```bash
      git commit -m "Add feature: short description"
      ```

### 4. Push Changes

- **Push your branch to the repository**:

    ```bash
    git push origin feature/my-feature-name
    ```

### 5. Pull Request

- Submit a **Pull Request** (PR) to the `main` branch
- Your PR will trigger CI/CD pipelines that run automated checks and tests

### 6. Review Process

- Address feedback from maintainers during code review.
- Once approved, your PR will be merged into the main branch.

## Troubleshooting

### Resolving "Unexpected Character" Error During Application Execution or Docker Image Building

This error is usually caused by incorrect encoding of `.env` files. To resolve the issue, follow these steps:

## Steps to Fix the Encoding Issue

1. **Open the `.env` file in a text editor** (e.g., Visual Studio Code).
2. **Check and change the encoding**:
   - Click on the encoding information in the bottom-right corner of the VS Code window.
   - Select **"Save with Encoding"**.
   - Choose **"UTF-8"** from the list (ensure it's not "UTF-8 with BOM").
3. **Save the file** with the correct encoding.
4. **Restart the application** using the command
   **`make run`**.

## Code of Conduct

Please follow our [Code of Conduct](code-of-conduct.md) when interacting with other contributors.
!!! success "Thank You"
    Thank you for contributing to Nest! Your contributions help make this project better for everyone.
