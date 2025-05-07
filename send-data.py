import requests
import time
import uuid
import argparse
from faker import Faker

ENDPOINT = "http://192.168.1.234:30080/send"


def send_request(iteration, payload):
    payload = payload.copy()
    payload["id"] = str(uuid.uuid4())  # unikalne ID
    response = requests.post(ENDPOINT, json=payload)
    print(f"Iteration: {iteration} Status: {response.status_code}")

def main(rate, duration, faker):
    interval = 1.0 / rate
    total_requests = int(rate * duration)

    print(f"Sending {total_requests} requests over {duration} seconds at rate {rate} req/sec...")
    for i in range(total_requests):
        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "adress": faker.address(),
            "message": faker.text()
        }

        start = time.time()
        send_request(i, payload)
        elapsed = time.time() - start
        sleep_time = max(0, interval - elapsed)
        time.sleep(sleep_time)

if __name__ == "__main__":
    faker = Faker()
    parser = argparse.ArgumentParser(description="Rate-limited sender to Flask Kafka endpoint")
    parser.add_argument("--rate", type=float, required=True, help="Number of requests per second")
    parser.add_argument("--duration", type=int, default=10, help="Duration to send requests in seconds")
    args = parser.parse_args()

    main(args.rate, args.duration, faker)
