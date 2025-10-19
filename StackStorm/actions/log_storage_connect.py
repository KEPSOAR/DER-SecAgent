import os
from google.cloud.sql.connector import Connector
import sqlalchemy
import pymysql.cursors
from sqlalchemy.sql import text

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/hancom.share.ants/KEPSOAR/auth.json"

connector = Connector()
def getconn() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        "mineral-style-454006-n9:us-central1:kepsoar",
        "pymysql",
        user="root",
        password="@RUDals000411",
        db="log_storage"
    )
    return conn


pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

with pool.connect() as db_conn:
    with db_conn.begin():
        result = db_conn.execute(
            text("SELECT * FROM log WHERE id=:log_id"),
            {"log_id": 1}
        ).fetchall()
        print(result)
        db_conn.commit()
        print(result[0][0])
        [id, event_time, device_ip, device_name, source_institution_code, source_ip, source_port, source_asset_name, source_country, source_mac, dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country, dest_mac, protocol, action, attack_type, account, risk_level] = result[0]
