import json
import time
import os
import logging
from enum import Enum
from faker import Faker
from kafka import KafkaProducer

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

def send_fake_data(producer: KafkaProducer, faker: Faker, topic: str) -> None:
    """
    Generuje losowe dane a za pomocą obiektu Faker a następnie wysyła je do Kafka za pomocą obiektu KafkaProducer

    Args:
        producer (KafkaProducer): Instancja klasy KafkaProducer
        faker (Faker): Instancja klasy Faker
        topic (str): Nazwa topic w Kafka na jaki wysłąne mają zostać dane

    Returns:
        None: Funkcja nie zwraca żadnej wartości
    """
    data = {
        "id": faker.uuid4(),
        "name": faker.name(),
        "email": faker.email(),
        "adress": faker.address(),
        "message": faker.text()
    }

    serialized_data = serialize_data(data)

    try:
        producer.send(topic=topic, value=serialized_data)
        logging.info(f"Wysłano dane: {data}")
    except Exception as e:
        logging.error(f"Wystąpił błąd podczas wysyłanie danych do Kafka: {e}")



if __name__ == "__main__":

    #Konfiguracja logowania
    logging_setup()

    # Utworznie obiektu KafkaProducer
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
        )
        logging.debug("Pomyślnie utworzone obiekt KafkaProducer")
    except Exception as e:
        logging.error(f"Wystąpił błąd podczas tworzenia obiektu KafkaProducer: {e}")
        exit(1)

    # Utworzenie obiektu Faker
    try:
        faker = Faker()
        logging.debug("Pomyślnie utworzono obiekt Faker")
    except Exception as e:
        logging.error(f"Wystąpił błąd podczas tworzenia obiektu Faker: {e}")
        exit(1)


    # Główna pętla działania aplikacji:
    while True:
        send_fake_data(producer=producer, faker=faker, topic=KAFKA_TOPIC)
        time.sleep(5)
