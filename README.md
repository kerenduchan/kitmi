# gql-kitmi

## Setup

`python kitmi.py init`

Create the sqlite database file (kitmi.db). Also creates the key.txt file,
which is used in order to encrypt/decrypt the username/password of each 
account.

## Create account(s)

`python kitmi.py create_account -n <name> -s <max|leumi> -u <username> -p <password>`

## Sync

`python kitmi.py sync -s <project_root_dir>/scraper/scrape.js`

Fetches data (transactions) from all accounts and stores it in the database.

## Run the graphql server

`uvicorn app:app --reload --host '::'`

Then browse to: http://0.0.0.0:8000/graphql#

## Architecture

Graphql + async sqlalchemy + sqlite
