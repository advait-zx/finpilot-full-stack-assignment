# GitHub setup and commit plan

The assignment expects meaningful Git history. Do not pretend the repository existed earlier than it did; start Git now and make logical commits by concern.

From the project root:

```powershell
git init
git branch -M main
```

Suggested logical history:

```powershell
# 1. Local platform and repository skeleton
git add .gitignore .env.example docker-compose.yml backend/Dockerfile frontend/Dockerfile frontend/package.json frontend/tsconfig*.json frontend/vite.config.ts frontend/index.html
git commit -m "chore: scaffold FinPilot local stack"

# 2. PostgreSQL schema, migrations and bootstrap data
git add backend/alembic* backend/app/models backend/app/db data/accounts.csv data/customers.csv data/data_dictionary.csv data/goals.csv data/holdings_snapshot.csv data/instruments.csv data/risk_profiles.csv data/transactions.csv
git commit -m "feat: add PostgreSQL schema migrations and seed pipeline"

# 3. Backend API and import validation
git add backend/app/api backend/app/core backend/app/schemas backend/app/services backend/app/main.py backend/requirements.txt backend/pyproject.toml
git commit -m "feat: implement authenticated portfolio and import API"

# 4. React user experience
git add frontend/src frontend/.env.example
git commit -m "feat: build customer portfolio goals and admin UI"

# 5. Tests, CI and documentation
git add backend/tests .github README.md DECISIONS.md docs scripts data/transactions_import_demo.csv
git commit -m "test: add validation coverage CI and reviewer documentation"
```

Create the GitHub repository, then connect and push using the repository URL GitHub gives you:

```powershell
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

After pushing, open GitHub Actions and wait for the CI workflow. Only claim CI evidence after a real run is green. If it fails, fix the actual error and push a normal follow-up commit.
