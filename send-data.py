
import requests
import time
import uuid
import argparse
from faker import Faker
from concurrent.futures import ThreadPoolExecutor, as_completed

ENDPOINT = "http://192.168.1.234:30080/send"

def send_request(iteration, faker):
    payload = {
        "id": str(uuid.uuid4()),
        "name": faker.name(),
        "email": faker.email(),
        "adress": faker.address(),
        "message": faker.text()
    }
    try:
        response = requests.post(ENDPOINT, json=payload)
        print(f"Iteration: {iteration} Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Iteration: {iteration} Error: {e}")

def main(rate, duration, faker, max_workers=50):
    total_requests = int(rate * duration)
    interval = 1.0 / rate

    print(f"Sending {total_requests} requests over {duration} seconds at rate {rate} req/sec using {max_workers} threads...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        start_time = time.time()

        for i in range(total_requests):
            future = executor.submit(send_request, i, faker)
            futures.append(future)
            # Rozkładanie w czasie
            time.sleep(interval)

        # Czekamy na wszystkie odpowiedzi
        for future in as_completed(futures):
            pass

    print("Done.")

if __name__ == "__main__":
    faker = Faker()
    parser = argparse.ArgumentParser(description="Rate-limited sender to Flask Kafka endpoint")
    parser.add_argument("--rate", type=float, required=True, help="Number of requests per second")
    parser.add_argument("--duration", type=int, default=10, help="Duration to send requests in seconds")
    parser.add_argument("--threads", type=int, default=50, help="Max number of concurrent threads")
    args = parser.parse_args()

    main(args.rate, args.duration, faker, max_workers=args.threads)

