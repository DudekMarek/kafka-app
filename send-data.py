

import requests
import time
import uuid
import argparse
from faker import Faker
from concurrent.futures import ThreadPoolExecutor

ENDPOINT = "http://192.168.1.234:30080/send"

def send_request(faker):
    payload = {
        "id": str(uuid.uuid4()),
        "name": faker.name(),
        "email": faker.email(),
        "adress": faker.address(),
        "message": faker.text()
    }
    try:
        requests.post(ENDPOINT, json=payload)
        return True
    except requests.exceptions.RequestException:
        return False

def main(rate, duration, faker, max_workers=50):
    total_requests = int(rate * duration)
    interval = 1.0 / rate
    start_time = time.time()
    completed = 0
    executor = ThreadPoolExecutor(max_workers=max_workers)
    futures = []

    print(f"Wysyłanie {total_requests} zapytań przez {duration} sekund z częstotliwością {rate} zapytań/sec")

    next_send_time = start_time

    for _ in range(total_requests):
        now = time.time()
        if now < next_send_time:
            time.sleep(next_send_time - now)
        else:
            pass

        future = executor.submit(send_request, faker)
        futures.append(future)
        next_send_time += interval

        # Co 1 sekunda — aktualizacja
        if time.time() - start_time >= 1:
            done = sum(1 for f in futures if f.done())
            elapsed = time.time() - start_time
            rps = done / elapsed
            print(f"\rWykonane zapytania: {done}/{total_requests} | Realna ilość zapytań na sekundę: {rps:.2f}", end='', flush=True)

    # Poczekaj na zakończenie wszystkich
    for f in futures:
        f.result()

    print("\nZakończono")
if __name__ == "__main__":
    faker = Faker()
    parser = argparse.ArgumentParser(description="Rate-limited sender to Flask Kafka endpoint")
    parser.add_argument("--rate", type=float, required=True, help="Number of requests per second")
    parser.add_argument("--duration", type=int, default=10, help="Duration to send requests in seconds")
    parser.add_argument("--threads", type=int, default=50, help="Max number of concurrent threads")
    args = parser.parse_args()

    main(args.rate, args.duration, faker, max_workers=args.threads)

