import json
import os
import logging
from enum import Enum
from flask import Flask, request, jsonify
from kafka import KafkaProducer
from pydantic import BaseModel, EmailStr, ValidationError

# Konfiguracja środowiska
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVER", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "fake_data")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Konfiguracja logowania
class LogLevel(Enum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    @classmethod
    def from_string(cls, level_str: str):
        try:
            return cls[level_str]
        except KeyError:
            raise ValueError(f"Nieprawidłowy log level: {level_str}")

def logging_setup():
    try:
        log_level_value = LogLevel.from_string(LOG_LEVEL)
        logging.basicConfig(level=log_level_value.value, format="%(asctime)s - %(levelname)s - %(message)s")
    except ValueError as e:
        print(e)
        exit(1)

# Walidacja danych z użyciem Pydantic
class DataModel(BaseModel):
    id: str
    name: str
    email: str
    adress: str
    message: str

def serialize_data(data: dict, encode_standard: str = "utf-8") -> bytes:
    try:
        return json.dumps(data).encode(encode_standard)
    except Exception as e:
        logging.error(f"Serializacja nieudana: {e}")
        raise

# Flask app
app = Flask(__name__)

# Inicjalizacja producenta Kafka
logging_setup()
try:
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
except Exception as e:
    logging.error(f"Błąd tworzenia KafkaProducer: {e}")
    exit(1)

@app.route("/healthz", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/send", methods=["POST"])
def send_to_kafka():
    try:
        # Walidacja danych JSON
        json_data = request.get_json()
        data = DataModel(**json_data)

        # Serializacja i wysyłka do Kafka
        serialized = serialize_data(data.dict())
        producer.send(KAFKA_TOPIC, value=serialized)
        logging.info(f"Wysłano dane: {data.dict()}")
        return jsonify({"status": "success", "message": "Data sent to Kafka"}), 200

    except ValidationError as ve:
        return jsonify({"status": "error", "errors": ve.errors()}), 422
    except Exception as e:
        logging.error(f"Błąd wysyłania do Kafka: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
