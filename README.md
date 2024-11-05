# OWASP Nest

## Initial setup

1. Clone the repository code from <https://github.com/owasp/nest>.
1. Create `backend/.env/local` file and copy `backend/.env/template`'s contents into it.
1. Open `backend/.env/local` and change `DJANGO_CONFIGURATION` value to `Local`.
1. Go to <https://www.algolia.com/> and create a free account.
Create an Algolia app and update `DJANGO_ALGOLIA_API_KEY` and `DJANGO_ALGOLIA_APPLICATION_ID` in your `.env/local` file.
That's all you need in terms of Algolia app configuration. You can ignore their onboarding wizard instructions.
Just make sure the API key has index write permissions.
1. Run `make run` and leave it running. Wait until [Nest local](http://localhost:8000/api/v1) is responding.
1. In a new terminal session run `make load-data` to populate the database from `data/` fixtures.
1. In the same window run `make index-data`.
1. Check the data is available via API endpoints: [projects](http://localhost:8000/api/v1/owasp/search/project) and [issues](http://localhost:8000/api/v1/owasp/search/issue).

Optional steps (if you're going to manage or fetch data):

1. Run `make setup` to create a super user.
1. Create a GitHub [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
1. Open `backend/.env/local` and update `GITHUB_TOKEN` value.
1. Now you should be able to run `make sync` command that updates your local DB data.
