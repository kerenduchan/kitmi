import os

db_path = os.getenv("DB_PATH")
if db_path is None:
    db_path = "."

DB_FILENAME = f'{db_path}/kitmi.db'
