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

- **Docker**: Required for running the Nest instance - [Docker Documentation](https://docs.docker.com/)
- **pre-commit**: Required to automate code checks and apply fixes, ensuring consistent and high-quality code.  
  Install using:
  ```bash
  pip install pre-commit  # Via virtual environment
  apt install pre-commit  # Linux (Ubuntu/Debian)
  brew install pre-commit # macOS
  ```
- **WSL (Windows Subsystem for Linux)**: Required for Windows users to enable Linux compatibility - [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
  - The `make run` command requires WSL to function properly.
  - Must use the **WSL terminal**, not PowerShell.
  - Ensure WSL integration is enabled in Docker Desktop settings (`Resources → WSL Integration`).

---

## **Setting up the Environment**

### **Backend Environment Setup**
1. Create a local environment file:
   ```bash
   touch backend/.env
   ```
2. Copy the contents from the template:
   ```bash
   cat backend/.env.example > backend/.env
   ```
3. Open the `.env` file and update necessary values:
   ```plaintext
   DJANGO_CONFIGURATION=Local
   DJANGO_ALGOLIA_APPLICATION_ID=<your-algolia-id>
   DJANGO_ALGOLIA_WRITE_API_KEY=<your-algolia-api-key>
   ```

### **Frontend Environment Setup**
1. Create a local environment file:
   ```bash
   touch frontend/.env
   ```
2. Copy the template:
   ```bash
   cat frontend/.env.example > frontend/.env
   ```

<details>
  <summary>⚠️ Important Notes on Environment Files</summary>

  - Ensure all `.env` files are saved in **UTF-8 format without BOM** to prevent errors.
  - **Restart the application** after making any `.env` changes.
  - If you encounter an **"Unexpected Character"** error, check the encoding of your `.env` files.
  
  🔹 **Fix Encoding in VS Code**:
  1. Open the `.env` file.
  2. Click encoding info (bottom-right).
  3. Select **"Save with Encoding → UTF-8 (without BOM)"**.

  Restart the application:
  ```bash
  make run
  ```
</details>

---

## **Running the Project**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-account>/<nest-fork>
   ```

2. **Run the Application**:
   - Navigate to the project root directory.
   - Start the application:
     ```bash
     make run
     ```
   - Wait until [Nest local](http://localhost:8000/api/v1) is accessible.

3. **Load Initial Data**:
   ```bash
   make load-data
   ```

4. **Index Data**:
   ```bash
   make index-data
   ```

5. **Verify API Endpoints**:
   - [API](http://localhost:8000/api/v1/)
   - [GraphQL](http://localhost:8000/graphql/)

---

## **Optional Steps**
### **GitHub Data Fetch**
If you plan to fetch GitHub OWASP data locally:

1. **Create a Super User**:
   ```bash
   make setup
   ```

2. **Generate a GitHub Personal Access Token**:
   - Create a [GitHub token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

3. **Update `.env` File**:
   ```plaintext
   GITHUB_TOKEN=<your-github-token>
   ```

4. **Sync Local Database Data**:
   ```bash
   make sync-data
   ```

---

## **Code Quality Checks**
Nest enforces strict code quality standards:

```bash
make check
```

Your PR **won’t be reviewed** if it fails these checks.

---

## **Testing**
Run all tests before submitting a PR:

```bash
make test
```

Your PR **won’t be merged** if it fails these checks.

### **Test Coverage**
- Backend test coverage requirement: [pyproject.toml](https://github.com/OWASP/Nest/blob/main/backend/pyproject.toml)
- Frontend test coverage requirement: [jest.config.ts](https://github.com/OWASP/Nest/blob/main/frontend/jest.config.ts)

Ensure your changes **do not drop overall test coverage**.

---

## **Contributing Workflow**
### 1️⃣ Find Something to Work On
- Check open issues: [GitHub Issues](https://github.com/owasp/nest/issues)
- Ask maintainers before working on an issue.

### 2️⃣ Create a Branch
```bash
git checkout -b feature/my-feature-name
```

### 3️⃣ Make Changes and Commit
- Run checks:
  ```bash
  make check-test
  ```
- Commit changes:
  ```bash
  git commit -m "Add feature: short description"
  ```

### 4️⃣ Push Changes
```bash
git push origin feature/my-feature-name
```

### 5️⃣ Open a Pull Request (PR)
- Submit a **PR** to the `main` branch.
- PRs trigger automated CI/CD checks.

### 6️⃣ Review and Merge
- Address feedback from maintainers.
- Once approved, your PR will be merged.

---

## **Environment Variables Documentation**
### **Frontend**
| Variable             | Description                             | Example Value                        |
|----------------------|---------------------------------|----------------------------------|
| `VITE_API_URL`      | Base API URL                    | `http://localhost:8000/api/v1/` |
| `VITE_ENVIRONMENT`  | Deployment environment         | `local`, `staging`, `production` |
| `VITE_GRAPHQL_URL`  | GraphQL API URL                | `http://localhost:8000/graphql/` |
| `VITE_GTM_AUTH`     | Google Tag Manager auth        | `your-gtm-auth`                 |
| `VITE_GTM_ID`       | Google Tag Manager ID          | `your-gtm-id`                   |
| `VITE_SENTRY_DSN`   | Sentry DSN for error tracking | *(Optional, leave empty if unused)* |

### **Backend**
| Variable                   | Description                     |
|----------------------------|---------------------------------|
| `DJANGO_CONFIGURATION`     | Django environment setup       |
| `DJANGO_ALGOLIA_APPLICATION_ID` | Algolia app ID |
| `DJANGO_ALGOLIA_WRITE_API_KEY`  | Algolia write API key |
| `GITHUB_TOKEN`             | GitHub API token               |
| `DJANGO_SECRET_KEY`        | Django secret key             |
| `DJANGO_SENTRY_DSN`        | Sentry DSN for error tracking |

---

## **Code of Conduct**
Please follow our [Code of Conduct](https://github.com/OWASP/Nest/blob/main/CODE_OF_CONDUCT.md) when interacting with contributors.

---

🚀 **Thank you for contributing to Nest!** 🚀
