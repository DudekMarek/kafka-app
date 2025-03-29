FROM python:3.10-slim

WORKDIR /app

CMD requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD . /app

CMD ["python", "./kafka-producer.py"]
