# db.py
import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

# --- 1. Initialize the Pool ---
try:
    cpool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )
    if cpool:
        print("Database connection pool created successfully")
except Exception as e:
    print(f"Error creating connection pool: {e}")
    cpool = None

# --- 2. Helper: Close Resources Safely ---
def close_conn(conn, cur):
    if cur:
        cur.close()
    if conn:
        cpool.putconn(conn)

# --- 3. Read Data (SELECT) ---
def execute_read(query, params=None):
    """
    Executes a SELECT query.
    Returns: (data_list, error_message)
    """
    conn = None
    cur = None
    try:
        conn = cpool.getconn()
        cur = conn.cursor()
        cur.execute(query, params)
        data = cur.fetchall()
        return data, None
    except Exception as e:
        return None, str(e)
    finally:
        close_conn(conn, cur)

# --- 4. Change Data (INSERT, UPDATE, DELETE) ---
def execute_change(query, params=None, returning=False):
    """
    Executes INSERT/UPDATE/DELETE.
    Returns: (fetched_row, error_message) if returning=True
             (True, error_message) if returning=False
    """
    conn = None
    cur = None
    try:
        conn = cpool.getconn()
        cur = conn.cursor()
        cur.execute(query, params)
        
        result = True
        if returning:
            result = cur.fetchone()
            
        conn.commit()
        return result, None
    except Exception as e:
        if conn: conn.rollback()
        return None, str(e)
    finally:
        close_conn(conn, cur)
