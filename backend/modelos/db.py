import os
import urllib.parse
import psycopg2
from psycopg2 import Error


def _config():
    db_url = os.getenv("DB_URL")
    if db_url:
        parsed = urllib.parse.urlparse(db_url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 5432,
            "user": urllib.parse.unquote(parsed.username or "postgres"),
            "password": urllib.parse.unquote(parsed.password or ""),
            "dbname": parsed.path.lstrip("/") or "finanzas_personales",
        }
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "dbname": os.getenv("DB_NAME", "finanzas_personales"),
    }


DB_CONFIG = _config()


def get_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise RuntimeError(f"Error conectando a PostgreSQL: {e}")
