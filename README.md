# FastAPI String Analyzer

This project exposes a set of endpoints for analysing and managing strings using FastAPI and SQLModel. It now includes the assets needed to deploy on Heroku from a GitHub repository.

## Local Development

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and set a `DATABASE_URL`. If you omit the variable a local SQLite database (`app.db`) will be used automatically.

   ```env
   DATABASE_URL=sqlite:///app.db
   ```

4. Run the API locally with Uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

## Deploying to Heroku via GitHub

1. Commit all changes and push the repository to GitHub.
2. In Heroku, create a new application and connect it to your GitHub repo.
3. In the **Deploy** tab, enable automatic deploys (optional) and trigger a manual deploy.
4. In the **Settings** tab:
   - Reveal config vars and add any required variables, e.g. `DATABASE_URL` pointing to your Heroku Postgres database and optional `SQLALCHEMY_ECHO=false`.
   - If you provision a Heroku Postgres add-on, Heroku will populate `DATABASE_URL` automatically.
5. Once the build completes, click **Open App** to verify the API is running. The app will start using the command specified in the `Procfile`:

   ```Procfile
   web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}
   ```

### Running database migrations

This project currently uses SQLModel without Alembic migrations. Schema changes require manual updates or adding a migration tool before deploying.

## Available Scripts

- `uvicorn main:app --reload` – start the development server.
- `uvicorn main:app --host=0.0.0.0 --port=8000` – mirror the Heroku launch command locally.

## Testing

Tests are not included yet. Consider adding unit tests for string analysis functions and API endpoints before production deployment.
