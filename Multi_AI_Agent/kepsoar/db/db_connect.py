import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Supabase connection info
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port", "5432")
DB_NAME = os.getenv("dbname")

def get_connection():
    """Return a Supabase PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def fetch_log_storage(key: int):
    """Fetch a specific log by ID."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM log WHERE id = %s", (key,))
            result = dict_fetchall(cursor)
            for row in result:
                print(row)
        return result
    except Exception as e:
        print(f"Log fetch error: {e}")
        return []
    finally:
        conn.close()

def fetch_history_storage_by_key(key: int):
    """Fetch a specific history entry by ID."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM history WHERE id = %s", (key,))
            result = dict_fetchall(cursor)
            for row in result:
                print(row)
        return result
    except Exception as e:
        print(f"History fetch error: {e}")
        return []
    finally:
        conn.close()
