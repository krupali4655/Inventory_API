import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from contextlib import contextmanager


load_dotenv()

try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )
    if connection_pool:
        print("Database connection pool created successfully")
except Exception as e:
    print(f"Error creating connection pool: {e}")

@contextmanager
def get_db_connection():
    """
    Get a connection from the pool, yield it to the function,
    and automatically put it back when done.
    """
    connection = None
    try:
        connection = connection_pool.getconn()
        yield connection
    except Exception as e:
        print(f"Database error: {e}")
        raise e
    finally:
        if connection:
            connection_pool.putconn(connection)