import json
import time
import os
import logging
from enum import Enum
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVER", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC")
KAFKA_TOPIC_PRODUCER = os.environ.get("KAFKA_TOPIC_PRODUCER", "procesed_data")
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

def serialize_data(data: dict, encode_standard: str = "utf-8") -> bytes:
    """
    Serializuje dane do formatu JSON oraz koduje je w standardzie UTF-8

    Args:
        data (dict): Słownik z danymi do serializacji
        encode_standard (str, optional): Sandard kodowania bazowo UTF-8

    Returns:
        bytes: Dane zakodowane w formacie UTF-8
    """
    try:
        serialized_data = json.dumps(data).encode(encode_standard)
        logging.debug(f"Pomyślnie zserializowane dnne: {data}, dnae wyjściowe: {serialized_data}")
        return serialized_data
    except Exception as e:
        logging.error(f"Error podczas seriwlizowania danych: {e}")

def proces_data(data: dict) -> dict:
    """
    Procesuje dane wyciągając ze słownika Imie, Nazwisko i Adres e-mail 

    Args:
        data (dict): Słownik z danymi do procesowania

    Returns:
        dict: Przeprocesowane dane w postaci słownika zawierajćego imię nazwiso i adres e-mail 
    """
    try:
        first_name, second_name = data["name"].split(" ")
        logging.debug(f"Rozpoczęto procesowanie danych {data}")
        procesed_data = {
                "first_name": first_name,
                "second_name": second_name,
                "e-mail": data["email"]
                }
        logging.info(f"Przeprocesowane dane: {procesed_data}")
        return procesed_data
    except Exception as e:
        logging.exception(f"Nastąpił błąd przy procesowaniu danych: {e}")



def consume_data() -> None:
    """
    Główna funkcja odpowiedzialna za odczytywanie wiadomości z kafki
    """
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

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
                procesed_data = proces_data(data)
                serialized_data = serialize_data(procesed_data)
                producer.send(topic=KAFKA_TOPIC_PRODUCER, value=serialized_data)
            else:
                logging.warning(f"Nie udało się przetworzyć wiadomości: {message.value}")
    except KeyboardInterrupt:
        logging.info("Konsument zakończył działanie.")
    finally:
        consumer.close()


if __name__ == "__main__":
    logging_setup()
    time.sleep(5)

    consume_data()





