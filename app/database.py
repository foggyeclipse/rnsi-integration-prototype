import psycopg2
from psycopg2.extras import Json
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def get_db_connection():
    """Return new PostgreSQL connection with autocommit disabled."""
    try:
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
        )
        conn.autocommit = False
        return conn
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        raise


def save_records(identifier: str, records: list[dict]) -> int:
    """Insert records into dictionary_records table. Returns number of saved records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    count = 0

    try:
        for record in records:
            cursor.execute(
                """
                INSERT INTO dictionary_records (identifier, record)
                VALUES (%s, %s::jsonb)
                """,
                (identifier, Json(record)),
            )
            count += 1

        conn.commit()
        logger.info("Saved %d records for %s", count, identifier)
        return count

    except Exception as e:
        conn.rollback()
        logger.error("Insert failed for %s: %s", identifier, e)
        raise
    finally:
        cursor.close()
        conn.close()