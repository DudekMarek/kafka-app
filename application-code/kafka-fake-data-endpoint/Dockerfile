FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "kafka-fake-data-endpoint:app"]
