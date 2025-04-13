#!/bin/bash

# Ustawienie katalogu głównego projektu
ROOT_DIR=$(pwd)

# Ścieżki do aplikacji
PRODUCER_DIR="$ROOT_DIR/application-code/kafka-fake-data-producer"
CONSUMER_DIR="$ROOT_DIR/application-code/kafka-fake-data-consumer1"

# Nazwy obrazów (muszą pasować do tych, które są używane w docker-compose)
PRODUCER_IMAGE="kafka-fake-data-producer:0.0.1"
CONSUMER_IMAGE="kafka-fake-data-consumer1:0.0.1"

echo "🔄 Usuwanie starych kontenerów i obrazów..."

# Usuwanie istniejących kontenerów korzystających z tych obrazów
docker ps -a --filter ancestor=$PRODUCER_IMAGE --format "{{.ID}}" | xargs -r docker rm -f
docker ps -a --filter ancestor=$CONSUMER_IMAGE --format "{{.ID}}" | xargs -r docker rm -f

# Usuwanie starych obrazów
docker rmi -f $PRODUCER_IMAGE $CONSUMER_IMAGE 2>/dev/null

echo "📦 Budowanie nowych obrazów..."

# Budowanie nowych obrazów
docker build -t $PRODUCER_IMAGE $PRODUCER_DIR
docker build -t $CONSUMER_IMAGE $CONSUMER_DIR

# Przechodzimy do katalogu z docker-compose
COMPOSE_DIR="$ROOT_DIR/configuration-files/kafka-local-development"
cd $COMPOSE_DIR

echo "🚀 Uruchamianie docker-compose..."
docker compose up

echo "✅ Gotowe!"
