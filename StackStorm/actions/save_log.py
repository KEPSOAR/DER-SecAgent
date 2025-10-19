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

class SaveLog(Action):
    def run(self, event_time, device_ip, device_name, source_institution_code, source_ip, source_port, source_asset_name, source_country, source_mac, dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country, dest_mac, protocol, action, attack_type, account, risk_level):
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
                "INSERT INTO log (event_time, device_ip, device_name, source_institution_code, source_ip, source_port, source_asset_name, source_country, source_mac, dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country, dest_mac, protocol, action, attack_type, account, risk_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (event_time, device_ip, device_name, source_institution_code, source_ip, source_port, source_asset_name, source_country, source_mac, dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country, dest_mac, protocol, action, attack_type, account, risk_level)
            )

            last_inserted_id = cursor.fetchone()[0]
            print(last_inserted_id, end="")
            connection.commit()

            cursor.close()
            connection.close()

        except Exception as e:
            print(f"Failed to save log: {e}")
