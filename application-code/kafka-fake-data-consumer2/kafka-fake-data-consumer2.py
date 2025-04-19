import json
import time
import os
import logging
import psycopg2
from psycopg2 import sql
from enum import Enum
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVER", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "procesed_data")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
DB_NAME = os.environ.get("DB_NAME", "kafka-app")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

class LogLevel(Enum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    @classmethod
    def from_string(cls, level_str: str):
        """
        Metoda konwertuje string na odpowiedni poziom logowania klasy Enum

        Args:
            level_log (str): LogLevel w postaci stringa
        """
        try:
            level_enum = cls[level_str]
            return level_enum
        except KeyError:
            raise ValueError(f"Nieprawidłowy log level: {level_str}")


def logging_setup() -> None:
    """
    Tworzy bazową konfigurację logowania
    """
    try:
        log_level_value = LogLevel.from_string(LOG_LEVEL)
        logging.basicConfig(level=log_level_value.value, format="%(asctime)s - %(levelname)s - %(message)s")
        logging.info(f"Log level set to {LOG_LEVEL}")
    except ValueError as e:
        print(e)
        exit(1)

def deserialize_data(serialized_data: bytes) -> dict:
    """
    Funkcja deserializująca dane z kafki

    Args:
        serialized_data (bytes): Dane w postaci binernej zakodowane w utf-8

    Returns:
        dict: Zdekodowany json w postaci słownika
    """
    try:
        result = json.loads(serialized_data)
        logging.debug(f"Udałos się zdekodować dane {result}")
        return result
    except json.JSONDecodeError as e:
        logging.error(f"Nie udało się zdekodować danych: {e}")
        return {} 

def save_data_to_db(data: dict, conn) -> None:
    """
    Zapisuje przetworzone dane do bazy danych PostgreSQL.

    Args:
        data (dict): Przetworzone dane w formacie {'first_name': ..., 'second_name': ..., 'e-mail': ...}
        conn: Obiekt połączenia psycopg2 do bazy PostgreSQL

    Returns:
        None
    """
    try:
        with conn.cursor() as cursor:
            logging.debug(f"Rozpoczęto zapisywanie danych do bazy: {data}")
            insert_query = sql.SQL("""
                INSERT INTO users (first_name, second_name, email)
                VALUES (%s, %s, %s)
            """)
            cursor.execute(insert_query, (data["first_name"], data["second_name"], data["e-mail"]))
            conn.commit()
            logging.info(f"Pomyślnie zapisano dane do bazy: {data}")
    except Exception as e:
        logging.exception(f"Wystąpił błąd podczas zapisu danych do bazy: {e}")
        conn.rollback()

def consume_and_store(consumer, conn) -> None:
    """
    Główna funkcja konsumująca wiadomości z Kafka następnie zapisuje je do bazy danych

    Args:
        consumer: Obiekt KafkaConsumer
        conn: Połącznie do bazy danych
    """
    try:
        for message in consumer:
            data = deserialize_data(message.value)
            save_data_to_db(data, conn)

    except Exception as e:
        logging.error(f"Nastąpił błąd: {e}")
    finally:
        consumer.close()
        conn.close()

if __name__ == "__main__":
    
    logging_setup()
    time.sleep(5)

    conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
            )

    consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
    )

    consume_and_store(consumer, conn)
