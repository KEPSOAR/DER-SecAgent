import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Supabase 연결 정보
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port", "5432")
DB_NAME = os.getenv("dbname")

def get_connection():
    """Supabase PostgreSQL 데이터베이스 연결을 반환합니다."""
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
        print(f"데이터베이스 연결 오류: {e}")
        return None

def dict_fetchall(cursor):
    """커서의 결과를 dictionary 리스트로 변환합니다."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_log_storage(key: int):
    """ID로 특정 로그를 조회합니다."""
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
        print(f"로그 조회 오류: {e}")
        return []
    finally:
        conn.close()

def fetch_history_storage_by_key(key: int):
    """ID로 특정 히스토리를 조회합니다."""
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
        print(f"히스토리 조회 오류: {e}")
        return []
    finally:
        conn.close()

def fetch_history_storage(history_type: str):
    """공격 유형별로 최근 2개의 히스토리를 조회합니다."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM history WHERE attack_type = %s ORDER BY event_time DESC LIMIT 2",
                (history_type,)
            )
            result = dict_fetchall(cursor)
            for row in result:
                print(row)
        return result
    except Exception as e:
        print(f"히스토리 조회 오류: {e}")
        return []
    finally:
        conn.close()

def insert_log_entry():
    """새로운 로그 엔트리를 삽입합니다."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO log (
                    event_time,
                    device_ip,
                    device_name,
                    source_institution_code,
                    source_ip,
                    source_port,
                    source_asset_name,
                    source_country,
                    source_mac,
                    dest_institution_code,
                    dest_ip,
                    dest_port,
                    dest_asset_name,
                    dest_country,
                    dest_mac,
                    protocol,
                    action,
                    attack_type,
                    account,
                    risk_level
                ) VALUES (
                    NOW(),
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                "155.0.67.11",
                "Main Firewall",
                "KEP_DER_M_198",
                "155.38.191.100",
                1440,
                "John Doe",
                "South Korea",
                "00:11:22:AA:BB:CC",
                "KEP_CEN_122",
                "100.0.0.100",
                3068,
                "kep_der_12",
                "South Korea",
                "01:12:23:AB:BC:CD",
                "tcp",
                "allow",
                "Probe",
                None,
                "Low"
            ))
            conn.commit()
            print("Log entry inserted successfully.")
            return True
    except Exception as e:
        print(f"로그 삽입 오류: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def insert_history_entry():
    """새로운 히스토리 엔트리를 삽입합니다."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO history (
                    event_time,
                    device_ip,
                    device_name,
                    source_institution_code,
                    source_ip,
                    source_port,
                    source_asset_name,
                    source_country,
                    source_mac,
                    dest_institution_code,
                    dest_ip,
                    dest_port,
                    dest_asset_name,
                    dest_country,
                    dest_mac,
                    protocol,
                    action,
                    attack_type,
                    account,
                    risk_level,
                    given_script,
                    executed_script,
                    changed_reason,
                    caution_level
                ) VALUES (
                    NOW(),
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
            """, (
                "10.0.0.1",
                "Main Firewall",
                "KEP_DER_M_198",
                "10.0.0.100",
                40000,
                "John Doe",
                "South Korea",
                "00:11:22:AA:BB:CC",
                "KEP_CEN_122",
                "100.0.0.100",
                80,
                "str",
                "South Korea",
                "01:12:23:AB:BC:CD",
                "tcp",
                "allow",
                "Probe",
                "kim",
                1,
                "iptables -A INPUT -s 10.0.0.100 -p tcp --dport 80 -j REJECT",
                "iptables -A INPUT -s 10.0.0.100 -p tcp --dport 80 -j DROP",
                "Manual modification: Changed from REJECT to DROP.",
                True
            ))
            conn.commit()
            print("Probe log entry inserted successfully.")
            return True
    except Exception as e:
        print(f"히스토리 삽입 오류: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def fetch_all_logs():
    """모든 히스토리 로그를 조회합니다."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM history")
            rows = dict_fetchall(cursor)
            for row in rows:
                print(row)
        return rows
    except Exception as e:
        print(f"모든 로그 조회 오류: {e}")
        return []
    finally:
        conn.close()
