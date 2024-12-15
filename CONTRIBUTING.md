# Contributing to Nest

Thank you for considering contributing to the **OWASP Nest** project! This document provides guidelines to help you get started.

## About the Project

Nest is a full-stack web application built using:

- **Backend**: Python, Django
- **Frontend**: TypeScript, React, Tailwind CSS
- **Search**: Algolia

The project uses a **containerized approach** for both development and production environments. Docker is required to run Nest locally.

## Prerequisites

Before contributing, ensure you have the following installed:

1. **Docker**: Required for running the Nest instance - [Docker Documentation](https://docs.docker.com/).
2. **WSL (Windows Subsystem for Linux)**: Required for Windows users to enable Linux compatibility - [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/).

## Setting up the Project

For instructions on setting up the project locally, please refer to the [README.md](https://github.com/OWASP/Nest/blob/main/README.md) file in the repository.

## Code Quality Checks

Nest enforces **code quality** standards to ensure consistency and maintainability. You can run automated checks locally before pushing your changes:

```bash
make check
```

This command runs linters and other static analysis tools for both the frontend and backend.

## Testing

Our **CI/CD** pipelines automatically run tests against every Pull Request. However, you can (and should) run tests locally before submitting a PR:

```bash
make test
```

### Test Coverage

- There is a **minimum test coverage requirement** for the **backend** code -- see [pyproject.toml](https://github.com/OWASP/Nest/blob/main/backend/pyproject.toml).
- There is a **minimum test coverage requirement** for the **frontend** code -- see [jest.config.ts](https://github.com/OWASP/Nest/blob/main/frontend/jest.config.ts).
- Ensure your changes do not drop the overall test coverage percentage.

If you are adding new functionality, include relevant test cases.

---

## Contributing Workflow

### 1. Find Something to Work On

- Check the **Issues** tab for open issues: [https://github.com/owasp/nest/issues](https://github.com/owasp/nest/issues)
- If you want to work on something specific, create a new issue or comment on an existing one to let others know.

### 2. Create a Branch

Always create a feature branch for your work:

```bash
git checkout -b feature/my-feature-name
```

### 3. Make Changes and Commit

- Follow best practices for code style and testing.
- Add tests for any new functionality or changes to ensure proper coverage.
- Run the code quality checks:

  ```bash
  make check
  ```

- Run tests to ensure everything works correctly:

  ```bash
  make test
  ```

- Write meaningful commit messages:

  ```bash
  git commit -m "Add feature: short description"
  ```

### 4. Push Changes

Push your branch to the repository:

```bash
git push origin feature/my-feature-name
```

### 5. Open a Pull Request

- Submit a **Pull Request (PR)** to the `main` branch.
- Your PR will trigger CI/CD pipelines that run automated checks and tests.

### 6. Review and Merge

- Address feedback from maintainers during code review.
- Once approved, your PR will be merged into the main branch.

---

## Code of Conduct

Please follow the [Code of Conduct](https://github.com/OWASP/Nest/blob/main/CODE_OF_CONDUCT.md) when interacting with other contributors.

---

Thank you for contributing to Nest! Your contributions help make this project better for everyone.
