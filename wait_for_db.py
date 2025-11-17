import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(
                dbname="auth_service",
                user="postgres",
                password="demo123",
                host="auth-postgres",
                port="5432",
            )



            conn.close()
            print("✅ Database is ready!")
            break
        except OperationalError:
            print("⏳ Waiting for database to be ready...")
            time.sleep(2)

if __name__ == "__main__":
    wait_for_db()
