import json
import os
import logging
from enum import Enum
from kafka import KafkaProducer
from pydantic import BaseModel, ValidationError
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

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

# FastAPI app
app = FastAPI()

# Inicjalizacja producenta Kafka
logging_setup()
try:
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
except Exception as e:
    logging.error(f"Błąd tworzenia KafkaProducer: {e}")
    exit(1)

@app.get("/healthz")
def health_check():
    return "OK"

@app.post("/send")
def send_to_kafka(data: DataModel):
    try:
        # Serializacja i wysyłka do Kafka
        serialized = serialize_data(data.dict())
        producer.send(KAFKA_TOPIC, value=serialized)
        logging.info(f"Wysłano dane: {data.dict()}")
        return JSONResponse(status_code=200, content={"status": "success", "message": "Data sent to Kafka"})

    except ValidationError as ve:
        logging.error(f"Validation error: {ve.errors()}")
        raise HTTPException(status_code=422, detail="Validation Error")
    except Exception as e:
        logging.error(f"Błąd wysyłania do Kafka: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


