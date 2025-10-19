#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase table creation script
Creates log, report, history tables.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

def create_tables():
    """Create tables function"""
    try:
        # 데이터베이스 연결
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )

        cursor = connection.cursor()
        print("Database connection successful!")

        # Read SQL file
        with open('create_tables.sql', 'r', encoding='utf-8') as file:
            sql_script = file.read()

        # Execute SQL script
        cursor.execute(sql_script)
        connection.commit()

        print("Tables created successfully!")
        print("- log table")
        print("- history table")
        print("- report table")

        # Check created tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('log', 'history', 'report')
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print("\nCreated tables verified: {} tables".format(len(tables)))
        for table in tables:
            print("  ✓ {}".format(table[0]))

        # Check column information for each table
        for table_name in ['log', 'history', 'report']:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))

            columns = cursor.fetchall()
            print("\n{} table structure:".format(table_name))
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print("  - {}: {} ({})".format(col[0], col[1], nullable))

        cursor.close()
        connection.close()
        print("\nDatabase connection closed")

    except Exception as e:
        print("Error occurred: {}".format(e))
        if 'connection' in locals():
            connection.rollback()
            connection.close()

if __name__ == "__main__":
    print("Starting Supabase table creation...")
    create_tables()
