import json
import time
import os
import logging
from enum import Enum
from kafka import KafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVER", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "fake_data")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

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

def consume_data() -> None:
    """
    Główna funkcja odpowiedzialna za odczytywanie wiadomości z kafki
    """

    consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset="earliest",
            enable_auto_commit=True,

    )

    logging.info(f"Uruchomiono konsumenta dla topicu: {KAFKA_TOPIC}")

    try:
        for message in consumer:
            data = deserialize_data(message.value)
            if data:
                logging.info(f"Odebrano dane: {data}")
                #dodać logikę procesowania danych

            else:
                logging.warning(f"Nie udało się przetworzyć wiadomości: {message.value}")
    except KeyboardInterrupt:
        logging.info("Konsument zakończył działanie.")
    finally:
        consumer.close()


if __name__ == "__main__":
    logging_setup()

    consume_data()





