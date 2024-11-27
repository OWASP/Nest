# OWASP Nest

## Initial Setup

Follow these steps to set up the OWASP Nest application:

1. **Clone the Repository**:
   - Clone the repository code from GitHub using the following command:
     ```bash
     git clone https://github.com/owasp/nest
     ```

1. **Create Environment File**:
   - Navigate to the `backend` directory and create a local environment file:
     ```bash
     touch backend/.env/local
     ```
   - Copy the contents from the template file into your new local environment file:
     ```bash
     cp backend/.env/template backend/.env/local
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
   - In your terminal, navigate to the project directory and run the following command to start the application:
     ```bash
     make run
     ```
   - Leave this terminal session running and wait until you see that [Nest local](http://localhost:8000/api/v1) is responding.

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

### Optional Steps (for managing or fetching data):

If you plan to manage or fetch data, follow these additional steps:

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


## Linting and Formatting Setup

To ensure code quality, we utilize ESLint and Prettier with Husky for pre-commit hooks.

### Installing Dependencies

Make sure you have the necessary dependencies installed:

```bash
npm install --save-dev eslint prettier husky lint-staged eslint-plugin-react eslint-plugin-react-hooks @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-config-prettier eslint-plugin-prettier
```
### Configure Husky
To set up Husky for pre-commit hooks, run:

```bash
npm run prepare 
```

### Pre-commit Hook Script
Ensure the `.husky/pre-commit` file consists of the following content:

```bash
#!/bin/sh
# .husky/pre-commit
echo "Running pre-commit hook..."
echo "Running lint-staged..."
export NODE_OPTIONS="--max-old-space-size=4096"
npx lint-staged

# Optional: Run ESLint and Prettier directly for debugging
eslint . --fix --config eslint.config.js
prettier --write . 
```


### Linting and Formatting Commands
You can manually run ESLint and Prettier to check your setup:
   - To lint your code:
```bash
npx eslint . --fix --config eslint.config.js
```

  - To format your code with Prettier:
```bash
npx prettier --write . 
```

