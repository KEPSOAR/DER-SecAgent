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
class SaveHistory(Action):
    def run(self, agent_script, user_script, changed_reason, log_id, caution):
        try:
            connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DBNAME
            )

            cursor = connection.cursor()

            # Get log data
            cursor.execute("SELECT * FROM log WHERE id=%s", (log_id,))
            result = cursor.fetchone()
            [id, event_time, device_ip, device_name, source_institution_code, source_ip, source_port, source_asset_name, source_country, source_mac, dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country, dest_mac, protocol, action, attack_type, account, risk_level, created_at] = result

            # Insert into history table
            print(f"[DEBUG] Inserting data into HISTORY table with log_id: {log_id}")
            cursor.execute(
                "INSERT INTO history (event_time, device_ip, device_name, source_institution_code, source_ip, source_port, source_asset_name, source_country, source_mac, dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country, dest_mac, protocol, action, attack_type, account, risk_level, given_script, executed_script, changed_reason, caution_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (event_time, device_ip, device_name, source_institution_code, source_ip, source_port, source_asset_name, source_country, source_mac, dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country, dest_mac, protocol, action, attack_type, account, risk_level, agent_script, user_script, None if changed_reason == "" else changed_reason, 1 if caution == "True" else 0)
            )

            last_inserted_id = cursor.fetchone()[0]
            print(f"[SUCCESS] Data inserted into HISTORY table. New history ID: {last_inserted_id}")
            print(last_inserted_id, end="")
            connection.commit()

            cursor.close()
            connection.close()

        except Exception as e:
            print(f"Failed to save history: {e}")
