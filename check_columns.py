import os
from dotenv import load_dotenv
from extensions import db  # Ensure this points to your db instance

# Load environment variables
load_dotenv()

def check_elections_columns():
    with db.engine.connect() as connection:
        result = connection.execute("SELECT column_name FROM information_schema.columns WHERE table_name='elections';")
        columns = [row[0] for row in result]
        print("Columns in 'elections' table:", columns)

if __name__ == "__main__":
    check_elections_columns()
