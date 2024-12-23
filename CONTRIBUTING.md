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
1. **pre-commit**: Required to automate code checks and apply fixes, ensuring consistent and high-quality code. Install it using virtual environment with `pip install pre-commit` command, as OS package with `apt install pre-commit` / `brew install pre-commit` or any other method depending on your configuration.

1. **WSL (Windows Subsystem for Linux)**: Required for Windows users to enable Linux compatibility - [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/).
    1. The `make run` command requires WSL to function properly. Make sure WSL is installed and configured on your system.
    If you haven't installed WSL yet, follow [Microsoft's official guide](https://learn.microsoft.com/en-us/windows/wsl/install).
    1. You must use WSL terminal (not Windows PowerShell) otherwise there is no guarantee that Nest development environment will be set up as intended. Please do not report any issues if you use PowerShell for running the commands -- it's not the intended way to run Nest locally so the errors will not be accepted as bugs.
    1. Ensure WSL integration is enabled in Docker Desktop settings by checking `Resources -- WSL integration` in Docker application settings.

## Setting up the Project

Follow these steps to set up the OWASP Nest application:

1. **Fork the Repository**:
   - Fork <https://github.com/OWASP/Nest> repository using "Fork" button

1. **Clone the Repository**:
   - Clone the repository code from your GitHub account using the following command:

     ```bash
     git clone https://github.com/<your-account>/<nest-fork>
     ```

1. **Create Environment Files**:
   - Create a local environment file in the `backend` directory:

     ```bash
     touch backend/.env/local
     ```

   - Copy the contents from the template file into your new local environment file:

     ```bash
     cat backend/.env/template > backend/.env/local
     ```

   - Create a local environment file in the `frontend` directory:

     ```bash
     touch frontend/.env
     ```

   - Copy the contents from the template file into your new local environment file:

     ```bash
     cat frontend/.env.example > frontend/.env
     ```

1. **Configure Environment Variables**:
   - Open the `backend/.env/local` file in your preferred text editor and change the `DJANGO_CONFIGURATION` value to `Local`:

     ```plaintext
     DJANGO_CONFIGURATION=Local
     ```

1. **Set Up Algolia**:
   - Go to [Algolia](https://www.algolia.com/) and create a free account.
   - After creating an account, create an Algolia app.
   - Update your `.env/local` file with the following keys from your Algolia app:

   ```plaintext
   DJANGO_ALGOLIA_API_KEY=<your_algolia_api_key>
   DJANGO_ALGOLIA_APPLICATION_ID=<your_algolia_application_id>
   ```

   - Ensure that your API key has index write permissions. You can ignore any onboarding wizard instructions provided by Algolia.

1. **Run the Application**:
   - In your terminal, navigate to the project root directory (not `backend` and not `frontend` subdirectories -- you need the project root directory).
   Nest has backend and frontend related Makefiles in corresponding directories and all of them are included in the main
   [Makefile](https://github.com/OWASP/Nest/blob/main/Makefile) in the project root directory. Run the following command to start the application:

   ```bash
   make run
   ```

   - Leave this terminal session running and wait until you see that [Nest local](http://localhost:8000/api/v1) is responding.
   - Please note as we use containerazed approach this command must be run in parallel to other Nest commands you may want to use.
     You need to keep it running in the current terminal and use another terminal session for your work.

1. **Load Initial Data**:
   - Open a new terminal session and run the following command to populate the database with initial data from fixtures:

   ```bash
   make load-data
   ```

1. **Index Data**:
   - In the same terminal session, run the following command to index the data:

   ```bash
   make index-data
   ```

1. **Verify API Endpoints**:
   - Check that the data is available via these API endpoints:
     - [Projects Endpoint](http://localhost:8000/api/v1/owasp/search/project)
     - [Issues Endpoint](http://localhost:8000/api/v1/owasp/search/issue)

### Optional Steps (for fetching GitHub OWASP organization data)

If you plan to fetch GitHub OWASP data locally, follow these additional steps:

1. **Create a Super User**:
   - Run the following command to create a super user for accessing the admin interface:

  ```bash
  make setup
  ```

1. **Generate a GitHub Personal Access Token**:
    - Create a GitHub [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

1. **Update Environment Variables with GitHub Token**:
    - Open `backend/.env/local` again and update it with your GitHub token:

      ```plaintext
      GITHUB_TOKEN=<your_github_token>
      ```

1. **Sync Local Database Data**:
   - Now you should be able to run the following command to sync your local database data with GitHub:

   ```bash
   make sync
   ```

## Code Quality Checks

Nest enforces code quality standards to ensure consistency and maintainability. You can run automated checks locally before pushing your changes:

```bash
make check
```

This command runs linters and other static analysis tools for both the frontend and backend.
**Please note your PR won't be reviewed if it fails the code quality checks.**

## Testing

Our CI/CD pipelines automatically run tests against every Pull Request. You can run tests locally before submitting a PR:

```bash
make test
```

This command runs tests and checks that coverage threshold requirements are satisfied for both backend and frontend.
**Please note your PR won't be merged if it fails the code tests checks.**

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

- Check that your commits include only related and intended changes. Do not include unrelated files.
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
