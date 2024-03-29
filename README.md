# kitmi

Kitmi is a basic web-based personal finance management tool.

Functionality:
- Fetches data from bank and credit card accounts
- Stores the data in a DB
- Allows you to categorize each payee / transaction
- Shows a balance report and expense charts

This repo contains the backend (sqlite DB, python, Strawberry GraphQL API)

The frontend (Vue) can be found here: https://github.com/kerenduchan/kitmi-ui 

## Installation

```
pip install -r requirements.txt
cd scraper
npm install
cd ..
```

## Create account(s)

```
python server/kitmi.py create_account -n <name> -s <max|leumi> -u <username> -p <password>
```

## Sync

```
python server/kitmi.py sync -s <project_root_dir>/scraper/scrape.js
```

Fetches data (transactions) from all accounts and stores it in the database.

## Run the graphql server

```
uvicorn app:app --app-dir server --reload
```

Then browse to: http://127.0.0.0:8000

## Architecture

- FastAPI
- Strawberry Graphql
- SQLAlchemy async
- SQLite
