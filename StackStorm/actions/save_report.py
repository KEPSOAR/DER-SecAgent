import os
import psycopg2
from dotenv import load_dotenv
from st2common.runners.base_action import Action # type: ignore

# Load environment variables from .env
load_dotenv('/opt/stackstorm/packs/kepsoar/.env')

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
class SaveReport(Action):
    def run(self, report):
        try:
            connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DBNAME
            )

            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO report (report) VALUES (%s) RETURNING id",
                (report,)
            )

            last_inserted_id = cursor.fetchone()[0]
            print(last_inserted_id, end="")
            connection.commit()

            cursor.close()
            connection.close()

        except Exception as e:
            print(f"Failed to save report: {e}")
