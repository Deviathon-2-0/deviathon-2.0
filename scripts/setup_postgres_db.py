import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_postgres():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname='imaira_db'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE imaira_db")
        print("Created database: imaira_db")
    else:
        print("Database imaira_db already exists.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_postgres()

